#!/bin/bash
for dir in programs/*/; do (cd "$dir" && make clean); done
