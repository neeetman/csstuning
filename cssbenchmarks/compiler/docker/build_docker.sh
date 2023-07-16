#!/bin/bash
set -e
image_name="compiler-benchmark:0.1"
echo "Building docker image $image_name"

if docker image inspect "$image_name" >/dev/null 2>&1; then
    echo "$image_name exists, do you want to remove it? [Y/n]"
    read answer
    if [ "$answer" != "${answer#[Yy]}" ]; then
        container_id=$(docker ps -aq --filter "ancestor=$image_name")
        if [ -n "$container_id" ]; then
            echo "Remove running container $container_id"
            docker container rm "$container_id"
        fi
        docker rmi "$image_name"
    fi
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