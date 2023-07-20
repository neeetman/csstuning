/**
 * trmm.c: This file is part of the PolyBench/C 3.2 test suite.
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
#include "trmm.h"

#include "cssbench.h"

/* Array initialization. */
static
void init_array(int n,
		DATA_TYPE *alpha,
		DATA_TYPE POLYBENCH_2D(A,N,N,n,n),
		DATA_TYPE POLYBENCH_2D(B,N,N,n,n))
{
  int i, j;

  *alpha = 32412;
  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++) {
      A[i][j] = ((DATA_TYPE) i*j) / n;
      B[i][j] = ((DATA_TYPE) i*j) / n;
    }
}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static
void print_array(int n,
		 DATA_TYPE POLYBENCH_2D(B,N,N,n,n))
{
  int i, j;

  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++) {
	fprintf (stderr, DATA_PRINTF_MODIFIER, B[i][j]);
	if ((i * n + j) % 20 == 0) fprintf (stderr, "\n");
    }
  fprintf (stderr, "\n");
}


/* Main computational kernel. The whole function will be timed,
   including the call and return. */
static
void kernel_trmm(int n,
		 DATA_TYPE alpha,
		 DATA_TYPE POLYBENCH_2D(A,N,N,n,n),
		 DATA_TYPE POLYBENCH_2D(B,N,N,n,n))
{
  int i, j, k;

#pragma scop
  /*  B := alpha*A'*B, A triangular */
  for (i = 1; i < _PB_N; i++)
    for (j = 0; j < _PB_N; j++)
      for (k = 0; k < i; k++)
        B[i][j] += alpha * A[i][k] * B[j][k];
#pragma endscop

}


int main(int argc, char** argv)
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
  DATA_TYPE alpha;
  POLYBENCH_2D_ARRAY_DECL(A,DATA_TYPE,N,N,n,n);
  POLYBENCH_2D_ARRAY_DECL(B,DATA_TYPE,N,N,n,n);

  /* Initialize array(s). */
  init_array (n, &alpha, POLYBENCH_ARRAY(A), POLYBENCH_ARRAY(B));

  /* Start timer. */
  polybench_start_instruments;

  /* Run kernel. */
  
CSSBenchStartCounter(0);
  for (int i = 0; i < repeat; i++)
      kernel_trmm (n, alpha, POLYBENCH_ARRAY(A), POLYBENCH_ARRAY(B));
  CSSBenchStopCounter(0);

  /* Stop and print timer. */
  polybench_stop_instruments;
  polybench_print_instruments;

  /* Prevent dead-code elimination. All live-out data must be printed
     by the function call in argument. */
  polybench_prevent_dce(print_array(n, POLYBENCH_ARRAY(B)));

  /* Be clean. */
  POLYBENCH_FREE_ARRAY(A);
  POLYBENCH_FREE_ARRAY(B);
  CSSBenchDumpState();
  CSSBenchFinish();

  return 0;
}
