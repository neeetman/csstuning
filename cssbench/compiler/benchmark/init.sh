#!/bin/bash

mkdir -p utilities/papi
mkdir -p utilities/polybench

tar -xzf packages/papi701.tar.gz -C utilities/papi
tar -xzf packages/polybench.tar.gz -C utilities/polybench

pushd utilities/papi/src/src
./configure --prefix=$PWD/../..
make && make install
popd

pushd utilities/polybench/src
make
popd

rm -rf utilities/papi/src
rm -rf utilities/polybench/src

