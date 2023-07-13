CC ?= gcc
CFLAGS ?= -I.
OUT_DIR := ./lib

SRC := benchwrapper.c
OBJ := $(OUT_DIR)/benchwrapper.o

LIB := $(OUT_DIR)/libbenchwrapper.a

all: $(LIB)

$(LIB): $(OBJ)
	ar rcs $@ $^

$(OBJ): $(SRC)
	mkdir -p $(OUT_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

.PHONY: clean

clean:
	rm -rf $(OUT_DIR)
