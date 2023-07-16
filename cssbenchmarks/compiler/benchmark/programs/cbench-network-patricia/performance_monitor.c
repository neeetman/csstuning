#include <stdio.h>
#include <stdlib.h>

#include <benchwrapper.h>


extern int main1(int argc, char* argv[], int print);

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

    ret = main1(argc, argv, 1);
    for (long i = 1; i < repeat; i++)
        ret = main1(argc, argv, 0);

    WrapperClockEnd(0);

    WrapperDumpState();
    WrapperFinish();

    return ret;
}
