#include <stdio.h>
#include <stdlib.h>

#include <benchwrapper.h>


extern int main1(int argc, char* argv[]);

int main(int argc, char* argv[])
{
    const char* envRepeatTimes = getenv("BENCH_REPEAT_MAIN");
    long repeat=1;
    int ret=0;

    if (envRepeatTimes != NULL) {
        repeat = atol(envRepeatTimes);
    }

    WrapperInit(1,0);

    WrapperClockStart(0);

    for (long i = 0; i < repeat; i++)
        ret = main1(argc, argv);

    WrapperClockEnd(0);
    WrapperDumpState();
    WrapperFinish();

    return ret;
}