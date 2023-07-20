#include <stdio.h>
#include <stdlib.h>

#include <cssbench.h>


extern int main1(int argc, char *argv[], int print);

int main(int argc, char* argv[])
{
    const char* envRepeatTimes = getenv("BENCH_REPEAT_MAIN");
    long repeat=1;
    int ret=0;

    if (envRepeatTimes != NULL) {
        repeat = atol(envRepeatTimes);
    }

    CSSBenchInit(1,0);
    CSSBenchStartCounter(0);

    ret = main1(argc, argv, 1);
    for (long i = 1; i < repeat; i++)
        ret = main1(argc, argv, 0);

    CSSBenchStopCounter(0);

    CSSBenchDumpState();
    CSSBenchFinish();

    return ret;
}
