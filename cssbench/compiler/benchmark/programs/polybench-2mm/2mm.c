/**
 * 2mm.c: This file is part of the PolyBench/C 3.2 test suite.
 *
 *
 * Contact: Louis-Noel Pouchet <pouchet@cse.ohio-state.edu>
 * Web address: http://polybench.sourceforge.net
 *
 * Updated by Grigori Fursin (http://cTuning.org/lab/people/gfursin)
 * to work with Collective Mind, OpenME plugin interface and
 * Collective Knowledge Frameworks for automatic, machine-learning based
 * and collective tuning and data mining: http://cTuning.org
 *
 * Further modified by An Shao (anshaohac@gmail.com)
 * to work with CSSTuning libraries and frameworks.
 */
#ifndef WINDOWS
#include <unistd.h>
#endif

#include <stdio.h>
#include <string.h>
#include <math.h>

/* Include polybench common header. */
#include "polybench.h"

/* Include benchmark-specific header. */
/* Default data type is double, default size is 4000. */
#include "2mm.h"

#include <cssbench.h>

/* Array initialization. */
static void init_array(int ni, int nj, int nk, int nl,
                       DATA_TYPE *alpha,
                       DATA_TYPE *beta,
                       DATA_TYPE POLYBENCH_2D(A, NI, NK, ni, nl),
                       DATA_TYPE POLYBENCH_2D(B, NK, NJ, nk, nj),
                       DATA_TYPE POLYBENCH_2D(C, NL, NJ, nl, nj),
                       DATA_TYPE POLYBENCH_2D(D, NI, NL, ni, nl))
{
  int i, j;

  *alpha = 32412;
  *beta = 2123;
  for (i = 0; i < ni; i++)
    for (j = 0; j < nk; j++)
      A[i][j] = ((DATA_TYPE)i * j) / ni;
  for (i = 0; i < nk; i++)
    for (j = 0; j < nj; j++)
      B[i][j] = ((DATA_TYPE)i * (j + 1)) / nj;
  for (i = 0; i < nl; i++)
    for (j = 0; j < nj; j++)
      C[i][j] = ((DATA_TYPE)i * (j + 3)) / nl;
  for (i = 0; i < ni; i++)
    for (j = 0; j < nl; j++)
      D[i][j] = ((DATA_TYPE)i * (j + 2)) / nk;
}

/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static void print_array(int ni, int nl,
                        DATA_TYPE POLYBENCH_2D(D, NI, NL, ni, nl))
{
  int i, j;
  int n = ni;

  if (nl < ni)
    n = nl;

  for (i = 0; i < n; i++)
  {
    printf(DATA_PRINTF_MODIFIER, D[i][j]);
    printf("\n");
  }
}

/* Main computational kernel. The whole function will be timed,
   including the call and return. */
static void kernel_2mm(int ni, int nj, int nk, int nl,
                       DATA_TYPE alpha,
                       DATA_TYPE beta,
                       DATA_TYPE POLYBENCH_2D(tmp, NI, NJ, ni, nj),
                       DATA_TYPE POLYBENCH_2D(A, NI, NK, ni, nk),
                       DATA_TYPE POLYBENCH_2D(B, NK, NJ, nk, nj),
                       DATA_TYPE POLYBENCH_2D(C, NL, NJ, nl, nj),
                       DATA_TYPE POLYBENCH_2D(D, NI, NL, ni, nl))
{
  int i, j, k;

#pragma scop
  /* D := alpha*A*B*C + beta*D */
  for (i = 0; i < _PB_NI; i++)
    for (j = 0; j < _PB_NJ; j++)
    {
      tmp[i][j] = 0;
      for (k = 0; k < _PB_NK; ++k)
        tmp[i][j] += alpha * A[i][k] * B[k][j];
    }
  for (i = 0; i < _PB_NI; i++)
    for (j = 0; j < _PB_NL; j++)
    {
      D[i][j] *= beta;
      for (k = 0; k < _PB_NJ; ++k)
        D[i][j] += tmp[i][k] * C[k][j];
    }
#pragma endscop
}

int main(int argc, char **argv)
{
  /* Retrieve problem size. */
  int ni = NI;
  int nj = NJ;
  int nk = NK;
  int nl = NL;

  const char *envRepeatTimes = getenv("BENCH_REPEAT_MAIN");
  long repeat = 1;
  int ret = 0;

  if (envRepeatTimes != NULL)
  {
    repeat = atol(envRepeatTimes);
  }

  CSSBenchInit(1, 0);

  /* Variable declaration/allocation. */
  DATA_TYPE alpha;
  DATA_TYPE beta;
  POLYBENCH_2D_ARRAY_DECL(tmp, DATA_TYPE, NI, NJ, ni, nj);
  POLYBENCH_2D_ARRAY_DECL(A, DATA_TYPE, NI, NK, ni, nk);
  POLYBENCH_2D_ARRAY_DECL(B, DATA_TYPE, NK, NJ, nk, nj);
  POLYBENCH_2D_ARRAY_DECL(C, DATA_TYPE, NL, NJ, nl, nj);
  POLYBENCH_2D_ARRAY_DECL(D, DATA_TYPE, NI, NL, ni, nl);

  /* Start timer. */
  polybench_start_instruments;

  /* Run kernel. */
  CSSBenchStartCounter(0);
  for (int i = 0; i < repeat; i++)
  {
    /* Initialize array(s). */
    init_array(ni, nj, nk, nl, &alpha, &beta,
               POLYBENCH_ARRAY(A),
               POLYBENCH_ARRAY(B),
               POLYBENCH_ARRAY(C),
               POLYBENCH_ARRAY(D));

    kernel_2mm(ni, nj, nk, nl,
               alpha, beta,
               POLYBENCH_ARRAY(tmp),
               POLYBENCH_ARRAY(A),
               POLYBENCH_ARRAY(B),
               POLYBENCH_ARRAY(C),
               POLYBENCH_ARRAY(D));
  }
  CSSBenchStopCounter(0);

  /* Stop and print timer. */
  polybench_stop_instruments;
  polybench_print_instruments;

  /* Prevent dead-code elimination. All live-out data must be printed
     by the function call in argument. */
  polybench_prevent_dce(print_array(ni, nl, POLYBENCH_ARRAY(D)));

  /* Be clean. */
  POLYBENCH_FREE_ARRAY(tmp);
  POLYBENCH_FREE_ARRAY(A);
  POLYBENCH_FREE_ARRAY(B);
  POLYBENCH_FREE_ARRAY(C);
  POLYBENCH_FREE_ARRAY(D);

  CSSBenchDumpState();
  CSSBenchFinish();

  return 0;
}
