
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <sys/time.h>
#include <sys/resource.h>

# define MYTIMER1 double
# define MYTIMER2 struct timeval
static MYTIMER1 *timerStarts; /* for intel cpu timer */
static MYTIMER2 *timerBefores, timerAfter;

static int numTimers=0;
static double *timerSeconds;

static int numVars=0;
static char **vars;

static char* timefile="tmp_timer.json";

void WrapperInit(int ntimer, int nvar)
{
    numTimers = ntimer;
    numVars = nvar;

    /* Initialize timers */
    if (numTimers > 0) {
        timerSeconds = malloc((numTimers + 1) * sizeof(double));
        timerStarts = malloc((numTimers + 1) * sizeof(MYTIMER1));   
        timerBefores = malloc(numTimers * sizeof(MYTIMER2));

        for (int i = 0; i < numTimers; i++) {
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
}

void WrapperClockStart(int timer)
{
#ifdef __INTEL_COMPILERX
    timerStarts[timer] = (double)_rdtsc();
#else
    gettimeofday(&timerBefores[timer], NULL);
#endif
}

void WrapperClockEnd(int timer)
{
#ifdef __INTEL_COMPILERX
    timerSeconds[timer] = ((double)((double)_rdtsc() - timerStarts[timer])) / (double) getCPUFreq();
#else
    gettimeofday(&timerAfter, NULL);
    timerSeconds[timer] = (timerAfter.tv_sec - timerBefores[timer].tv_sec) + (timerAfter.tv_usec - timerBefores[timer].tv_usec)/1000000.0;
#endif
}

void WrapperAddVarI(int i, char* desc, int svar)
{
    sprintf(vars[i], desc, svar);
}

void WrapperAddVarF(int i, char* desc, float svar)
{
    sprintf(vars[i], desc, svar);
}

void WrapperAddVarD(int i, char* desc, double svar)
{
    sprintf(vars[i], desc, svar);
}

void WrapperAddVarS(int i, char* desc, void* svar)
{
    sprintf(vars[i], desc, svar);
}

void WrapperDumpState(void)
{
    FILE* f = fopen(timefile, "w");
    if (f == NULL) {
        printf("Error: can't open timer file %s for writing\n", timefile);
        exit(1);
    }

    fprintf(f, "{\n");

    if (numTimers > 0) {
        fprintf(f," \"execution_time_0\":%.6lf", timerSeconds[0]);
        for (int i = 1; i < numTimers; i++) {
        fprintf(f,",\n \"execution_time_%u\":%.6lf", i, timerSeconds[i]);
        }
    }

    // Max memory usage in KB
    struct rusage ru; 
    getrusage(RUSAGE_SELF, &ru);
    fprintf(f,",\n \"maxrss\":%ld", ru.ru_maxrss);

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
}

double WrapperGetTimer(int timer)
{
    return timerSeconds[timer];
}

void WrapperFinish(void)
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
}
