# Declarations
BENCHWAPPER_PATH = ../../benchwrapper

ZCC ?= gcc
LDCC ?= gcc

CFLAGS ?= -I$(BENCHWAPPER_PATH)
CFLAGS_ADD ?=  

LDFLAGS ?= -lm -L$(BENCHWAPPER_PATH)/lib -lbenchwrapper
LDFLAGS_ADD ?=

# Files
SRC := $(wildcard *.c)
OBJ := $(patsubst %.c,%.o,$(SRC))

# Targets
a.out: $(OBJ)
	$(LDCC) -o $@ $^ $(LDFLAGS) $(LDFLAGS_ADD)
	
%.o: %.c
	$(ZCC) $(CFLAGS) $(CFLAGS_ADD) -c $< -o $@

.PHONY: all clean

all: a.out

clean:
	rm -rf $(OBJ) a.out
