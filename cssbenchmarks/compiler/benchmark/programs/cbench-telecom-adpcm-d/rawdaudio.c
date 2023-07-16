/* testd - Test adpcm decoder */

#include "adpcm.h"
#include <stdio.h>
#include <stdlib.h>

#include <benchwrapper.h>

struct adpcm_state state;

#define NSAMPLES 1000

char	abuf[NSAMPLES/2];
short	sbuf[NSAMPLES];

int main()
{
    int n;

    const char* envRepeatTimes = getenv("BENCH_REPEAT_MAIN");
    long repeat=1;
    int ret=0;

    if (envRepeatTimes != NULL) {
        repeat = atol(envRepeatTimes);
    }

    WrapperInit(1, 0);
    WrapperClockStart(0);

    while(1) {
        struct adpcm_state current_state = state;

	n = read(0, abuf, NSAMPLES/2);
	if ( n < 0 ) {
	    perror("input file");
	    exit(1);
	}
	if ( n == 0 ) break;
  
        /* gfursin */
        for (int i = 0; i < repeat; i++)
        {
	  /* The call to adpcm_decoder modifies the state. We need to make a
	     copy of the state and to restore it before each iteration of the
	     kernel to make sure we do not alter the output of the
	     application. */
          state = current_state;
  	  adpcm_decoder(abuf, sbuf, n*2, &state);  /* modifies state */
	}

	write(1, sbuf, n*4);
    }

    WrapperClockEnd(0);
    WrapperDumpState();
    WrapperFinish();
    return 0;
}
