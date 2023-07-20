/**
 * jacobi-1d-imper.c: This file is part of the PolyBench/C 3.2 test suite.
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
/* Default data type is double, default size is 100x10000. */
#include "jacobi-1d-imper.h"

#include "cssbench.h"

/* Array initialization. */
static
void init_array (int n,
		 DATA_TYPE POLYBENCH_1D(A,N,n),
		 DATA_TYPE POLYBENCH_1D(B,N,n))
{
  int i;

  for (i = 0; i < n; i++)
      {
	A[i] = ((DATA_TYPE) i+ 2) / n;
	B[i] = ((DATA_TYPE) i+ 3) / n;
      }
}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static
void print_array(int n,
		 DATA_TYPE POLYBENCH_1D(A,N,n))

{
  int i;

  for (i = 0; i < n; i++)
    {
      fprintf(stderr, DATA_PRINTF_MODIFIER, A[i]);
      if (i % 20 == 0) fprintf(stderr, "\n");
    }
  fprintf(stderr, "\n");
}


/* Main computational kernel. The whole function will be timed,
   including the call and return. */
static
void kernel_jacobi_1d_imper(int tsteps,
			    int n,
			    DATA_TYPE POLYBENCH_1D(A,N,n),
			    DATA_TYPE POLYBENCH_1D(B,N,n))
{
  int t, i, j;

#pragma scop
  for (t = 0; t < _PB_TSTEPS; t++)
    {
      for (i = 1; i < _PB_N - 1; i++)
	B[i] = 0.33333 * (A[i-1] + A[i] + A[i + 1]);
      for (j = 1; j < _PB_N - 1; j++)
	A[j] = B[j];
    }
#pragma endscop

}


int main(int argc, char** argv)
{
  /* Prepare ctuning vars */

  /* Retrieve problem size. */
  int n = N;
  int tsteps = TSTEPS;

  const char *envRepeatTimes = getenv("BENCH_REPEAT_MAIN");
  long repeat = 1;
  int ret = 0;

  if (envRepeatTimes != NULL)
  {
    repeat = atol(envRepeatTimes);
  }
  CSSBenchInit(1, 0);

  /* Variable declaration/allocation. */
  POLYBENCH_1D_ARRAY_DECL(A, DATA_TYPE, N, n);
  POLYBENCH_1D_ARRAY_DECL(B, DATA_TYPE, N, n);


  /* Initialize array(s). */
  init_array (n, POLYBENCH_ARRAY(A), POLYBENCH_ARRAY(B));

  /* Start timer. */
  polybench_start_instruments;

  /* Run kernel. */
  CSSBenchStartCounter(0);
  for (int i = 0; i < repeat; i++)
      kernel_jacobi_1d_imper (tsteps, n, POLYBENCH_ARRAY(A), POLYBENCH_ARRAY(B));  
  
  CSSBenchStopCounter(0);

  /* Stop and print timer. */
  polybench_stop_instruments;
  polybench_print_instruments;

  /* Prevent dead-code elimination. All live-out data must be printed
     by the function call in argument. */
  polybench_prevent_dce(print_array(n, POLYBENCH_ARRAY(A)));

  /* Be clean. */
  POLYBENCH_FREE_ARRAY(A);
  POLYBENCH_FREE_ARRAY(B);

  CSSBenchDumpState();
  CSSBenchFinish();

  return 0;
}
