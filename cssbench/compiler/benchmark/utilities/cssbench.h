
#ifndef BENCHWRAPER_H_
#define BENCHWRAPER_H_

#ifdef __cplusplus
extern "C"
{
#endif

    extern void CSSBenchInit(int ncounter, int nvar);
    extern void CSSBenchStartCounter(int counter);
    extern void CSSBenchStopCounter(int counter);
    extern void CSSBenchFinish(void);

    extern void CSSBenchAddVarI(int i, char *desc, int svar);
    extern void CSSBenchAddVarF(int i, char *desc, float svar);
    extern void CSSBenchAddVarD(int i, char *desc, double svar);
    extern void CSSBenchAddVarS(int i, char *desc, void *svar);

    extern double CSSBenchGetTimer(int timer);
    extern void CSSBenchDumpState(void);

#define CSSBENCH_PAPI
#ifdef CSSBENCH_PAPI
    static void HandleError(char *file, int line, char *call, int retval);
    extern void InitPapi(int ncounter);
    extern void FinishPapi();
    extern void StartPapiCounter();
    extern void StopPapiCounter(int counter);
#endif

#ifdef __cplusplus
}
#endif

#endif