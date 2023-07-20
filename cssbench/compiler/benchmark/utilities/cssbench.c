#include "cssbench.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <sys/resource.h>

#ifdef CSSBENCH_PAPI
#include <papi.h>

#define MAX_NUM_EVENT 128

static int numPapiEvent = 0;
static int papiEventlist[MAX_NUM_EVENT] = { 0 };
static long_long **eventVals;
static int papiEventSet = PAPI_NULL;
#endif

# define MYTIMER1 double
# define MYTIMER2 struct timeval
static double *timerStarts; /* for intel cpu timer */
static MYTIMER2 *timerBefores, timerAfter;

static int numCounters = 0;
static double *timerSeconds;

static int numVars = 0;
static char **vars;

static char* resfile="tmp_result.json";
static char* eventsfile="papi_events.txt";

// #define DEBUG
#ifdef DEBUG
#define DBGLOG(...) fprintf(stdout, __VA_ARGS__)
#else
#define DBGLOG(...)
#endif

void CSSBenchInit(int ncounter, int nvar)
{
    numCounters = ncounter;
    numVars = nvar;

    /* Initialize timers and PAPI */
    if (numCounters > 0) {
        timerSeconds = malloc((numCounters + 1) * sizeof(double));
        timerStarts = malloc((numCounters + 1) * sizeof(MYTIMER1));   
        timerBefores = malloc(numCounters * sizeof(MYTIMER2));

        for (int i = 0; i < numCounters; i++) {
            timerSeconds[i] = 0.0;
            timerStarts[i] = 0.0;
        }

    }

    /* Initialize variables */
    if (numVars > 0) {
        vars = malloc((numVars + 1) * sizeof(char*)); 

        for (int i = 0; i < numVars; i++) {
        vars[i] = malloc(512 * sizeof(char));
        vars[i][0] = 0;
        }
    }

#ifdef CSSBENCH_PAPI
    InitPapi(ncounter);
#endif
}

void CSSBenchStartCounter(int counter)
{
#ifdef __INTEL_COMPILERX
    timerStarts[timer] = (double)_rdtsc();
#else
    gettimeofday(&timerBefores[counter], NULL);
#endif

#ifdef CSSBENCH_PAPI
    StartPapiCounter();
#endif
}

void CSSBenchStopCounter(int counter)
{
#ifdef __INTEL_COMPILERX
    timerSeconds[timer] = ((double)((double)_rdtsc() - timerStarts[timer])) / (double) getCPUFreq();
#else
    gettimeofday(&timerAfter, NULL);
    timerSeconds[counter] = (timerAfter.tv_sec - timerBefores[counter].tv_sec) + (timerAfter.tv_usec - timerBefores[counter].tv_usec)/1e6;
#endif

#ifdef CSSBENCH_PAPI
    StopPapiCounter(counter);
#endif
}

void CSSBenchAddVarI(int i, char* desc, int svar)
{
    sprintf(vars[i], desc, svar);
}

void CSSBenchAddVarF(int i, char* desc, float svar)
{
    sprintf(vars[i], desc, svar);
}

void CSSBenchAddVarD(int i, char* desc, double svar)
{
    sprintf(vars[i], desc, svar);
}

void CSSBenchAddVarS(int i, char* desc, void* svar)
{
    sprintf(vars[i], desc, svar);
}

void CSSBenchDumpState(void)
{
    FILE* f = fopen(resfile, "w");
    if (f == NULL) {
        printf("Error: can't open timer file %s for writing\n", resfile);
        exit(1);
    }

    fprintf(f, "{\n");

    if (numCounters > 0) {
        fprintf(f," \"execution_time\":%.6lf", timerSeconds[0]);
        DBGLOG("Execution time: %.6lf\n", timerSeconds[0]);

#ifdef CSSBENCH_PAPI
        char event_name[PAPI_MAX_STR_LEN];
        for (int j = 0; j < numPapiEvent; j++) {
            if (PAPI_event_code_to_name(papiEventlist[j], event_name) != PAPI_OK) 
                fprintf(stderr, "Error converting event code %d to name\n", papiEventlist[j]);
            else {
                DBGLOG("Event %d: %s %lld\n", j, event_name, eventVals[0][j]);
                fprintf(f,",\n \"%s\":%lld", event_name, eventVals[0][j]);
            }
        }
#endif

        for (int i = 1; i < numCounters; i++) {
            fprintf(f,",\n \"execution_time_%u\":%.6lf", i, timerSeconds[i]);
            DBGLOG("Execution time: %.6lf\n", timerSeconds[i]);

#ifdef CSSBENCH_PAPI
            for (int j = 0; j < numPapiEvent; j++) {
                if (PAPI_event_code_to_name(papiEventlist[j], event_name) != PAPI_OK) 
                    fprintf(stderr, "Error converting event code %d to name\n", papiEventlist[j]);
                else {
                    DBGLOG("Event %d: %s_%u %lld\n", j, event_name, i, eventVals[i][j]);
                    fprintf(f,",\n \"%s_%u\":%lld", event_name, i, eventVals[i][j]);
                } 
            }
#endif

        }
    }
    
    // Max memory usage in KB
    struct rusage ru; 
    getrusage(RUSAGE_SELF, &ru);
    fprintf(f,",\n \"maxrss\":%ld", ru.ru_maxrss);
    DBGLOG("Max memory usage: %ld\n", ru.ru_maxrss);

    if (numVars > 0) {
        fprintf(f,",\n \"run_time_state\":{\n");

        for (int i = 0; i < numVars; i++) {
            if ((vars[i][0]!=0)) {
                if (i != 0) fprintf(f, ",\n");
                fprintf(f,"  %s", vars[i]);
            }
        }

        fprintf(f,"\n }");
    }

    fprintf(f,"\n}\n");

    fclose(f);

    DBGLOG("Dumping state to file %s done\n", resfile);
}

double CSSBenchGetTimer(int timer)
{
    return timerSeconds[timer];
}

void CSSBenchFinish(void)
{
    for (int i = 0; i < numVars; i++) {
        free(vars[i]);
    }
    free(vars);

    free(timerSeconds);
    free(timerStarts);
#ifdef MYTIMER2
    free(timerBefores);
#endif

#ifdef CSSBENCH_PAPI
    FinishPapi();
#endif
}

#ifdef CSSBENCH_PAPI

static void HandleError(char *file, int line, char *call, int retval)
{
    fprintf(stderr,"Error: %-40s:line #%d\n", file, line);
    fprintf(stderr, "Error %d in %s: %s\n", retval, call, PAPI_strerror(retval));

    if (PAPI_is_initialized())
        PAPI_shutdown();

    exit(retval);
}

int LoadAndAddEventsFromFile(const char* filename) {
    FILE* file = fopen(filename, "r");
    if (file == NULL) {
        fprintf(stderr, "Error opening file %s\n", filename);
        exit(1);
    }

    char line[PAPI_MAX_STR_LEN];
    int i = 0;
    int retval;
    while (fgets(line, sizeof(line), file) != NULL && i < MAX_NUM_EVENT) {
        // Remove trailing newline
        line[strcspn(line, "\n")] = 0;

        if ((retval = PAPI_event_name_to_code(line, papiEventlist + i)) != PAPI_OK) {
            fclose(file);
            fprintf(stderr, "Error converting PAPI event name %s to code\n", line);
            HandleError(__FILE__, __LINE__, "PAPI_event_name_to_code", retval);
        }

        if ((retval = PAPI_add_event(papiEventSet, papiEventlist[i])) != PAPI_OK) {
            // HandleError(__FILE__, __LINE__, "PAPI_add_event", retval);
            fprintf(stderr, "Error adding PAPI event %s\n retval: %d", line, retval);
            continue;
        }   
        
        fprintf(stdout, "Added PAPI event %s\n", line);
        i++;
    }

    fclose(file);

    return i;  // Return the total number of events
}

void InitPapi(int ncounter)
{
    int retval;
    if((retval = PAPI_library_init(PAPI_VER_CURRENT)) != PAPI_VER_CURRENT ) {
		fprintf(stderr, "Error: PAPI_library_init failed\n");
    	exit(1);
    }

    if ((retval = PAPI_create_eventset (&papiEventSet)) != PAPI_OK)
        HandleError(__FILE__, __LINE__, "PAPI_create_eventset", retval);
    
    numPapiEvent = LoadAndAddEventsFromFile(eventsfile);
    DBGLOG("Loaded %d events from %s\n", numPapiEvent, eventsfile);
    if (numPapiEvent == 0) {
        return;
    }

    //if ((retval = PAPI_add_events(papiEventSet, papiEventlist, numPapiEvent)) != PAPI_OK)
    //    HandleError(__FILE__, __LINE__, "PAPI_add_events", retval);

    eventVals = malloc(sizeof(long_long*) * ncounter);
    for (int i = 0; i < ncounter; i++) {
        eventVals[i] = malloc(sizeof(long_long) * numPapiEvent);
        memset(eventVals[i], 0, sizeof(long_long) * numPapiEvent);
    }
}

void FinishPapi() 
{
    DBGLOG("Finishing PAPI\n");
    int retval;
    long long values[MAX_NUM_EVENT];

    if (numPapiEvent == 0) {
        if ((retval = PAPI_destroy_eventset(&papiEventSet)) != PAPI_OK)
            HandleError(__FILE__, __LINE__, "PAPI_destroy_eventset", retval);

        PAPI_shutdown();
        return;
    }

    if ((retval = PAPI_cleanup_eventset(papiEventSet)) != PAPI_OK)
        HandleError(__FILE__, __LINE__, "PAPI_cleanup_eventset", retval);

    if ((retval = PAPI_destroy_eventset(&papiEventSet)) != PAPI_OK)
        HandleError(__FILE__, __LINE__, "PAPI_destroy_eventset", retval);

    PAPI_shutdown();

    // free eventVals
    for (int i = 0; i < numCounters; i++) {
        free(eventVals[i]);
    }
    free(eventVals);
}

void StartPapiCounter()
{
    if (numPapiEvent == 0) {
        return;
    }

    int retval;
    if ((retval = PAPI_start(papiEventSet)) != PAPI_OK)
        HandleError(__FILE__, __LINE__, "PAPI_start", retval);
}

void StopPapiCounter(int counter)
{
    if (numPapiEvent == 0) {
        return;
    }

    int retval;

    if ((retval = PAPI_stop(papiEventSet, eventVals[counter])) != PAPI_OK)
        HandleError(__FILE__, __LINE__, "PAPI_stop", retval);
}

/* PAPI */
#endif
