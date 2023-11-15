#!/bin/bash

mkdir -p ${PAPI_DIR}
mkdir -p ${POLYBENCH_DIR}

tar -xzf packages/papi701.tar.gz -C ${PAPI_DIR}
tar -xzf packages/polybench.tar.gz -C ${POLYBENCH_DIR}

pushd ${PAPI_DIR}/src/src
./configure --prefix=${PAPI_DIR}
make && make install
echo 0 | tee /proc/sys/kernel/perf_event_paranoid
popd

pushd ${POLYBENCH_DIR}/src
make
popd

rm -rf ${PAPI_DIR}/src ${POLYBENCH_DIR}/src
rm -f packages/papi701.tar.gz packages/polybench.tar.gz
