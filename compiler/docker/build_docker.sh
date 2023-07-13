#!/bin/bash
set -e
image_name="compiler-benchmark:0.1"

if docker image inspect "$image_name" >/dev/null 2>&1; then
    echo "$image_name exists, remove it first"
    docker container rm $(docker container ls -a -q --filter "ancestor=$image_name")
    docker rmi "$image_name"
fi

echo "Building $image_name"

cd "$( dirname "${BASH_SOURCE[0]}" )"

BUILD_DIR=$(mktemp -d)
trap "rm -rf $BUILD_DIR" EXIT

echo "Using temporary build directory $BUILD_DIR"
cp -r ../benchmark $BUILD_DIR
cp Dockerfile $BUILD_DIR

echo "Building docker image"
docker build -t $image_name \
    -f "$BUILD_DIR/Dockerfile"\
    "$BUILD_DIR"

echo "Done"