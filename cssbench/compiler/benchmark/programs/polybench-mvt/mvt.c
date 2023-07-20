/**
 * mvt.c: This file is part of the PolyBench/C 3.2 test suite.
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
#include "mvt.h"

#include "cssbench.h"

/* Array initialization. */
static void init_array(int n,
                       DATA_TYPE POLYBENCH_1D(x1, N, n),
                       DATA_TYPE POLYBENCH_1D(x2, N, n),
                       DATA_TYPE POLYBENCH_1D(y_1, N, n),
                       DATA_TYPE POLYBENCH_1D(y_2, N, n),
                       DATA_TYPE POLYBENCH_2D(A, N, N, n, n))
{
  int i, j;

  for (i = 0; i < n; i++)
  {
    x1[i] = ((DATA_TYPE)i) / n;
    x2[i] = ((DATA_TYPE)i + 1) / n;
    y_1[i] = ((DATA_TYPE)i + 3) / n;
    y_2[i] = ((DATA_TYPE)i + 4) / n;
    for (j = 0; j < n; j++)
      A[i][j] = ((DATA_TYPE)i * j) / N;
  }
}

/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static void print_array(int n,
                        DATA_TYPE POLYBENCH_1D(x1, N, n),
                        DATA_TYPE POLYBENCH_1D(x2, N, n))

{
  int i;

  for (i = 0; i < n; i++)
  {
    fprintf(stderr, DATA_PRINTF_MODIFIER, x1[i]);
    fprintf(stderr, DATA_PRINTF_MODIFIER, x2[i]);
    if (i % 20 == 0)
      fprintf(stderr, "\n");
  }
}

/* Main computational kernel. The whole function will be timed,
   including the call and return. */
static void kernel_mvt(int n,
                       DATA_TYPE POLYBENCH_1D(x1, N, n),
                       DATA_TYPE POLYBENCH_1D(x2, N, n),
                       DATA_TYPE POLYBENCH_1D(y_1, N, n),
                       DATA_TYPE POLYBENCH_1D(y_2, N, n),
                       DATA_TYPE POLYBENCH_2D(A, N, N, n, n))
{
  int i, j;

#pragma scop
  for (i = 0; i < _PB_N; i++)
    for (j = 0; j < _PB_N; j++)
      x1[i] = x1[i] + A[i][j] * y_1[j];
  for (i = 0; i < _PB_N; i++)
    for (j = 0; j < _PB_N; j++)
      x2[i] = x2[i] + A[j][i] * y_2[j];
#pragma endscop
}

int main(int argc, char **argv)
{
  /* Prepare ctuning vars */

  /* Retrieve problem size. */
  int n = N;

  const char *envRepeatTimes = getenv("BENCH_REPEAT_MAIN");
  long repeat = 1;
  int ret = 0;

  if (envRepeatTimes != NULL)
  {
    repeat = atol(envRepeatTimes);
  }
  CSSBenchInit(1, 0);

  /* Variable declaration/allocation. */
  POLYBENCH_2D_ARRAY_DECL(A, DATA_TYPE, N, N, n, n);
  POLYBENCH_1D_ARRAY_DECL(x1, DATA_TYPE, N, n);
  POLYBENCH_1D_ARRAY_DECL(x2, DATA_TYPE, N, n);
  POLYBENCH_1D_ARRAY_DECL(y_1, DATA_TYPE, N, n);
  POLYBENCH_1D_ARRAY_DECL(y_2, DATA_TYPE, N, n);

  /* Initialize array(s). */
  init_array(n,
             POLYBENCH_ARRAY(x1),
             POLYBENCH_ARRAY(x2),
             POLYBENCH_ARRAY(y_1),
             POLYBENCH_ARRAY(y_2),
             POLYBENCH_ARRAY(A));

  /* Start timer. */
  polybench_start_instruments;

  /* Run kernel. */

  CSSBenchStartCounter(0);
  for (int i = 0; i < repeat; i++)
    kernel_mvt(n,
               POLYBENCH_ARRAY(x1),
               POLYBENCH_ARRAY(x2),
               POLYBENCH_ARRAY(y_1),
               POLYBENCH_ARRAY(y_2),
               POLYBENCH_ARRAY(A));
  CSSBenchStopCounter(0);

  /* Stop and print timer. */
  polybench_stop_instruments;
  polybench_print_instruments;

  /* Prevent dead-code elimination. All live-out data must be printed
     by the function call in argument. */
  polybench_prevent_dce(print_array(n, POLYBENCH_ARRAY(x1), POLYBENCH_ARRAY(x2)));

  /* Be clean. */
  POLYBENCH_FREE_ARRAY(A);
  POLYBENCH_FREE_ARRAY(x1);
  POLYBENCH_FREE_ARRAY(x2);
  POLYBENCH_FREE_ARRAY(y_1);
  POLYBENCH_FREE_ARRAY(y_2);
  CSSBenchDumpState();
  CSSBenchFinish();

  return 0;
}
