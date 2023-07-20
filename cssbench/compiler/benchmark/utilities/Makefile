CC ?= gcc
CFLAGS ?= -I.
OUT_DIR := ./lib

SRC := cssbench.c
OBJ := $(OUT_DIR)/cssbench.o

LIB := $(OUT_DIR)/libcssbench.a

all: $(LIB)

$(LIB): $(OBJ)
	ar rcs $@ $^

$(OBJ): $(SRC)
	mkdir -p $(OUT_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

.PHONY: clean

clean:
	rm -rf $(OUT_DIR)
