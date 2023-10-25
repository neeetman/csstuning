#!/bin/bash

set -eu -o pipefail

BENCHBASE_PROFILES="${BENCHBASE_PROFILES:-mysql}"
CLEAN_BUILD="${CLEAN_BUILD:-true}"

scriptdir=$(dirname "$(readlink -f "$0")")
rootdir=$(readlink -f "$scriptdir/../../")

cd "$scriptdir"

docker build \
    --build-arg CONTAINERUSER_UID=$(id -u) \
    --build-arg CONTAINERUSER_GID=$(id -g) \
    -t your_image_name .