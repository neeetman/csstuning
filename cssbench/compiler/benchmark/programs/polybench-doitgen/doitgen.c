/**
 * doitgen.c: This file is part of the PolyBench/C 3.2 test suite.
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
#include "doitgen.h"

#include "cssbench.h"

/* Array initialization. */
static
void init_array(int nr, int nq, int np,
		DATA_TYPE POLYBENCH_3D(A,NR,NQ,NP,nr,nq,np),
		DATA_TYPE POLYBENCH_2D(C4,NP,NP,np,np))
{
  int i, j, k;

  for (i = 0; i < nr; i++)
    for (j = 0; j < nq; j++)
      for (k = 0; k < np; k++)
	A[i][j][k] = ((DATA_TYPE) i*j + k) / np;
  for (i = 0; i < np; i++)
    for (j = 0; j < np; j++)
      C4[i][j] = ((DATA_TYPE) i*j) / np;
}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static
void print_array(int nr, int nq, int np,
		 DATA_TYPE POLYBENCH_3D(A,NR,NQ,NP,nr,nq,np))
{
  int i, j, k;

  for (i = 0; i < nr; i++)
    for (j = 0; j < nq; j++)
      for (k = 0; k < np; k++) {
	fprintf (stderr, DATA_PRINTF_MODIFIER, A[i][j][k]);
	if (i % 20 == 0) fprintf (stderr, "\n");
      }
  fprintf (stderr, "\n");
}


/* Main computational kernel. The whole function will be timed,
   including the call and return. */
static
void kernel_doitgen(int nr, int nq, int np,
		    DATA_TYPE POLYBENCH_3D(A,NR,NQ,NP,nr,nq,np),
		    DATA_TYPE POLYBENCH_2D(C4,NP,NP,np,np),
		    DATA_TYPE POLYBENCH_3D(sum,NR,NQ,NP,nr,nq,np))
{
  int r, q, p, s;

#pragma scop
  for (r = 0; r < _PB_NR; r++)
    for (q = 0; q < _PB_NQ; q++)  {
      for (p = 0; p < _PB_NP; p++)  {
	sum[r][q][p] = 0;
	for (s = 0; s < _PB_NP; s++)
	  sum[r][q][p] = sum[r][q][p] + A[r][q][s] * C4[s][p];
      }
      for (p = 0; p < _PB_NR; p++)
	A[r][q][p] = sum[r][q][p];
    }
#pragma endscop

}


int main(int argc, char** argv)
{
  /* Retrieve problem size. */
  int nr = NR;
  int nq = NQ;
  int np = NP;

  const char *envRepeatTimes = getenv("BENCH_REPEAT_MAIN");
  long repeat = 1;
  int ret = 0;

  if (envRepeatTimes != NULL)
  {
    repeat = atol(envRepeatTimes);
  }

  CSSBenchInit(1, 0);

  /* Variable declaration/allocation. */
  POLYBENCH_3D_ARRAY_DECL(A,DATA_TYPE,NR,NQ,NP,nr,nq,np);
  POLYBENCH_3D_ARRAY_DECL(sum,DATA_TYPE,NR,NQ,NP,nr,nq,np);
  POLYBENCH_2D_ARRAY_DECL(C4,DATA_TYPE,NP,NP,np,np);

  /* Initialize array(s). */
  init_array (nr, nq, np,
	      POLYBENCH_ARRAY(A),
	      POLYBENCH_ARRAY(C4));

  /* Start timer. */
  polybench_start_instruments;

  /* Run kernel. */

  CSSBenchStartCounter(0);
  for (int i = 0; i < repeat; i++)
      kernel_doitgen (nr, nq, np,
                      POLYBENCH_ARRAY(A),
                      POLYBENCH_ARRAY(C4),
                      POLYBENCH_ARRAY(sum));

  CSSBenchStopCounter(0);

  polybench_stop_instruments;
  polybench_print_instruments;

  /* Prevent dead-code elimination. All live-out data must be printed
     by the function call in argument. */
  polybench_prevent_dce(print_array(nr, nq, np,  POLYBENCH_ARRAY(A)));

  /* Be clean. */
  POLYBENCH_FREE_ARRAY(A);
  POLYBENCH_FREE_ARRAY(sum);
  POLYBENCH_FREE_ARRAY(C4);

  CSSBenchDumpState();
  CSSBenchFinish();

  return 0;
}
