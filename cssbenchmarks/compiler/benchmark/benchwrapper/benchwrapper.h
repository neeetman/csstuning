
#ifndef BENCHWRAPER_H_
#define BENCHWRAPER_H_

#ifdef __cplusplus
extern "C"
{
#endif

void WrapperInit(int numTimers, int numVars);

void WrapperClockStart(int timer);
void WrapperClockEnd(int timer);

void WrapperAddVarI(int i, char* desc, int svar);
void WrapperAddVarF(int i, char* desc, float svar);
void WrapperAddVarD(int i, char* desc, double svar);
void WrapperAddVarS(int i, char* desc, void* svar);

double WrapperGetTimer(int timer);

void WrapperDumpState();

void WrapperFinish();

#ifdef __cplusplus
}
#endif

#endif