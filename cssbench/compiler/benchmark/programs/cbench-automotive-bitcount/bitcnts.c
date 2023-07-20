/* +++Date last modified: 05-Jul-1997 */

/*
**  BITCNTS.C - Test program for bit counting functions
**
**  public domain by Bob Stout & Auke Reitsma
*/

#include <cssbench.h>

#include <stdio.h>
#include <stdlib.h>
#include "conio.h"
#include <limits.h>
#include <time.h>
#include <float.h>
#include "bitops.h"

#define FUNCS 7

static int CDECL bit_shifter(long int x);

int main(int argc, char *argv[])
{
    int print = 1;

    /*   clock_t start, stop; */
    /*  double ct = 0.0; */
    /*     double cmin = DBL_MAX, cmax = 0;  */
    /*     int cminix, cmaxix; */
    long n, seed;
    int iterations;
    static int (*CDECL pBitCntFunc[FUNCS])(long) = {
        bit_count,
        bitcount,
        ntbl_bitcnt,
        ntbl_bitcount,
        /*            btbl_bitcnt, DOESNT WORK*/
        BW_btbl_bitcount,
        AR_btbl_bitcount,
        bit_shifter};
    static char *text[FUNCS] = {
        "Optimized 1 bit/loop counter",
        "Ratko's mystery algorithm",
        "Recursive bit count by nybbles",
        "Non-recursive bit count by nybbles",
        /*            "Recursive bit count by bytes",*/
        "Non-recursive bit count by bytes (BW)",
        "Non-recursive bit count by bytes (AR)",
        "Shift and count bits"};

    const char *envRepeatTimes = getenv("BENCH_REPEAT_MAIN");
    long repeat = 1;
    int ret = 0;

    if (envRepeatTimes != NULL)
    {
        repeat = atol(envRepeatTimes);
    }

    CSSBenchInit(1, 0);

    if (argc < 2)
    {
        fprintf(stderr, "Usage: bitcnts <iterations>\n");
        exit(EXIT_FAILURE);
    }
    iterations = atoi(argv[1]);

    if (print == 1)
        puts("Bit counter algorithm benchmark\n");

    CSSBenchStartCounter(0);

    for (int i = 0; i < repeat; i++)
    {
        for (int j = 0; j < FUNCS; j++)
        {
            /*FGG
                start = clock();

                for (j = n = 0, seed = rand(); j < iterations; j++, seed += 13)
            */

            for (int k = 0, n = 0, seed = 1; k < iterations; k++, seed += 13)
                n += pBitCntFunc[j](seed);

            /*FGG
                stop = clock();
                ct = (stop - start) / (double)CLOCKS_PER_SEC;
                if (ct < cmin) {
               cmin = ct;
               cminix = i;
                }
                if (ct > cmax) {
               cmax = ct;
               cmaxix = i;
                }

                printf("%-38s> Time: %7.3f sec.; Bits: %ld\n", text[i], ct, n);
            */
            if (print == 1)
            {
                printf("%-38s> Bits: %ld\n", text[i], n);
                print = 0;
            }
        }
    }
    CSSBenchStopCounter(0);
    /*FGG
      printf("\nBest  > %s\n", text[cminix]);
      printf("Worst > %s\n", text[cmaxix]);
    */

    CSSBenchDumpState();
    CSSBenchFinish();
    return 0;
}

static int CDECL bit_shifter(long int x)
{
    int i, n;

    for (i = n = 0; x && (i < (sizeof(long) * CHAR_BIT)); ++i, x >>= 1)
        n += (int)(x & 1L);
    return n;
}
