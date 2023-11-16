#!/bin/bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

mkdir -p results
mkdir -p ${PAPI_DIR}
mkdir -p ${POLYBENCH_DIR}

tar -xzf packages/papi701.tar.gz -C ${PAPI_DIR}
tar -xzf packages/polybench.tar.gz -C ${POLYBENCH_DIR}

pushd ${PAPI_DIR}/src/src
./configure --prefix=${PAPI_DIR}
make && make install
popd

pushd ${POLYBENCH_DIR}/src
make
popd

rm -rf ${PAPI_DIR}/src ${POLYBENCH_DIR}/src
rm -f packages/papi701.tar.gz packages/polybench.tar.gz
