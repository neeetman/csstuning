/**
 * syrk.c: This file is part of the PolyBench/C 3.2 test suite.
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
#include "syrk.h"

#include "cssbench.h"

/* Array initialization. */
static void init_array(int ni, int nj,
                       DATA_TYPE *alpha,
                       DATA_TYPE *beta,
                       DATA_TYPE POLYBENCH_2D(C, NI, NI, ni, ni),
                       DATA_TYPE POLYBENCH_2D(A, NI, NJ, ni, nj))
{
  int i, j;

  *alpha = 32412;
  *beta = 2123;
  for (i = 0; i < ni; i++)
    for (j = 0; j < nj; j++)
      A[i][j] = ((DATA_TYPE)i * j) / ni;
  for (i = 0; i < ni; i++)
    for (j = 0; j < ni; j++)
      C[i][j] = ((DATA_TYPE)i * j) / ni;
}

/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static void print_array(int ni,
                        DATA_TYPE POLYBENCH_2D(C, NI, NI, ni, ni))
{
  int i, j;

  for (i = 0; i < ni; i++)
    for (j = 0; j < ni; j++)
    {
      fprintf(stderr, DATA_PRINTF_MODIFIER, C[i][j]);
      if ((i * ni + j) % 20 == 0)
        fprintf(stderr, "\n");
    }
  fprintf(stderr, "\n");
}

/* Main computational kernel. The whole function will be timed,
   including the call and return. */
static void kernel_syrk(int ni, int nj,
                        DATA_TYPE alpha,
                        DATA_TYPE beta,
                        DATA_TYPE POLYBENCH_2D(C, NI, NI, ni, ni),
                        DATA_TYPE POLYBENCH_2D(A, NI, NJ, ni, nj))
{
  int i, j, k;

#pragma scop
  /*  C := alpha*A*A' + beta*C */
  for (i = 0; i < _PB_NI; i++)
    for (j = 0; j < _PB_NI; j++)
      C[i][j] *= beta;
  for (i = 0; i < _PB_NI; i++)
    for (j = 0; j < _PB_NI; j++)
      for (k = 0; k < _PB_NJ; k++)
        C[i][j] += alpha * A[i][k] * A[j][k];
#pragma endscop
}

int main(int argc, char **argv)
{
  /* Prepare ctuning vars */

  /* Retrieve problem size. */
  int ni = NI;
  int nj = NJ;

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
  POLYBENCH_2D_ARRAY_DECL(C, DATA_TYPE, NI, NI, ni, ni);
  POLYBENCH_2D_ARRAY_DECL(A, DATA_TYPE, NI, NJ, ni, nj);

  /* Initialize array(s). */
  init_array(ni, nj, &alpha, &beta, POLYBENCH_ARRAY(C), POLYBENCH_ARRAY(A));

  /* Start timer. */
  polybench_start_instruments;

  /* Run kernel. */

  CSSBenchStartCounter(0);
  for (int i = 0; i < repeat; i++)
    kernel_syrk(ni, nj, alpha, beta, POLYBENCH_ARRAY(C), POLYBENCH_ARRAY(A));
  CSSBenchStopCounter(0);

  /* Stop and print timer. */
  polybench_stop_instruments;
  polybench_print_instruments;

  /* Prevent dead-code elimination. All live-out data must be printed
     by the function call in argument. */
  polybench_prevent_dce(print_array(ni, POLYBENCH_ARRAY(C)));

  /* Be clean. */
  POLYBENCH_FREE_ARRAY(C);
  POLYBENCH_FREE_ARRAY(A);
  CSSBenchDumpState();
  CSSBenchFinish();

  return 0;
}
