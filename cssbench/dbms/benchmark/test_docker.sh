#!/bin/bash

export BENCHBASE_PROFILE='mysql'
benchmark='tpcc'

#git clone git@github.com:neeetman/benchbase.git

cd benchbase

export BENCHBASE_PROFILES=$BENCHBASE_PROFILE
export PROFILE_VERSION='latest'
export CLEAN_BUILD='false'
export SKIP_TESTS='true'

./docker/build-run-benchmark-with-docker.sh $benchmark

# rm -rf benchbase

echo 'Done!'