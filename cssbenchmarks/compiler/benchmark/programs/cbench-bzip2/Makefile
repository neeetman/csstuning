# Compiler type (GCC or LLVM)
COMPILER_TYPE = GCC
MACROS :=

# Source files
SRC = $(wildcard *.c)

# Object files
OBJ_GCC = $(SRC:.c=.o)
OBJ_LLVM = $(SRC:.c=.bc)

# Paths
BENCHWAPPER_PATH = ../../benchwrapper

OPTFLAGS = 

# GCC flags
CFLAGS_GCC = -I$(BENCHWAPPER_PATH) $(MACROS)
LDFLAGS_GCC = -lm -L$(BENCHWAPPER_PATH)/lib -lbenchwrapper

# LLVM flags
CFLAGS_LLVM = -c -emit-llvm -O0 -Xclang -disable-O0-optnone -I$(BENCHWAPPER_PATH) $(MACROS)
LDFLAGS_LLVM = -lm -L$(BENCHWAPPER_PATH)/lib -lbenchwrapper

# Targets
all: a.out

ifeq ($(COMPILER_TYPE),GCC)
a.out: $(OBJ_GCC)
	gcc -o $@ $^ $(LDFLAGS_GCC)
%.o: %.c
	gcc $(CFLAGS_GCC) $(OPTFLAGS) -c $< -o $@
else ifeq ($(COMPILER_TYPE),LLVM)
a.out: $(OBJ_LLVM)
	llvm-link $^ | llc -O1 -relocation-model=pic -o tmp.s
	clang -O0 -x assembler tmp.s -o $@ $(LDFLAGS_LLVM)
	rm tmp.s
%.bc: %.c
	clang $(CFLAGS_LLVM) $< -o $@
	opt -enable-new-pm=0 $(OPTFLAGS) -S $@ -o $@
endif

# Phony targets
.PHONY: all clean

# Clean the build
clean:
	rm -rf $(OBJ_GCC) $(OBJ_LLVM) a.out tmp*
