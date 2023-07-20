# Compiler type (GCC or LLVM)
COMPILER_TYPE = GCC
MACROS :=

# Source files
SRC = $(wildcard *.c)

# Object files
OBJ_GCC = $(SRC:.c=.o)
OBJ_LLVM = $(SRC:.c=.bc)

# Paths
UTILS_DIR = ../../utilities
PAPI_DIR = $(UTILS_DIR)/papi
POLYBENCH_DIR = $(UTILS_DIR)/polybench


OPTFLAGS = 
INCLUDE_FLAGS= -I$(UTILS_DIR) -I$(PAPI_DIR)/include -I$(POLYBENCH_DIR)/include 
LIB_FLAGS = -lm -L$(PAPI_DIR)/lib -lpapi -L$(POLYBENCH_DIR)/lib -lpolybench

# GCC flags
CFLAGS_GCC = $(INCLUDE_FLAGS) $(MACROS)
LDFLAGS_GCC = $(LIB_FLAGS)

# LLVM flags
CFLAGS_LLVM = -c -emit-llvm -O0 -Xclang -disable-O0-optnone $(INCLUDE_FLAGS) $(MACROS)
LDFLAGS_LLVM = $(LIB_FLAGS) 

# Targets
all: a.out

ifeq ($(COMPILER_TYPE),GCC)
a.out: $(OBJ_GCC) cssbench.o
	gcc -o $@ $^ $(LDFLAGS_GCC)
%.o: %.c
	gcc $(CFLAGS_GCC) $(OPTFLAGS) -c $< -o $@
cssbench.o: $(UTILS_DIR)/cssbench.c
	cp $(UTILS_DIR)/papi_events.txt .
	gcc $(CFLAGS_GCC) $(OPTFLAGS) -c $< -o $@

else ifeq ($(COMPILER_TYPE),LLVM)
a.out: $(OBJ_LLVM) cssbench.bc
	llvm-link $^ | llc -O1 -relocation-model=pic -o tmp.s
	clang -O0 -x assembler tmp.s -o $@ $(LDFLAGS_LLVM)
	rm tmp.s
%.bc: %.c
	clang $(CFLAGS_LLVM) $< -o $@
	opt -enable-new-pm=0 $(OPTFLAGS) -S $@ -o $@
cssbench.bc: $(UTILS_DIR)/cssbench.c
	cp $(UTILS_DIR)/papi_events.txt .
	clang $(CFLAGS_LLVM) $< -o $@
	opt -enable-new-pm=0 $(OPTFLAGS) -S $@ -o $@
endif

# Phony targets
.PHONY: all clean

# Clean the build
clean:
	rm -rf $(OBJ_GCC) $(OBJ_LLVM) a.out tmp* papi_events.txt *.bc *.o
