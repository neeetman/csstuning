#!/bin/bash
for dir in programs/*/; do (cd "$dir" && make clean); done

rm -rf utilities/papi utilities/polybench
