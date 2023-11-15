#!/bin/bash
set -euo pipefail

image_name="csstuning-compiler:0.1"

echo "Building docker image $image_name"

if docker image inspect "$image_name" >/dev/null 2>&1; then
    echo "$image_name exists, do you want to remove it? [Y/n]"
    read answer
    if [ "$answer" != "${answer#[Yy]}" ]; then
        container_id=$(docker ps -aq --filter "ancestor=$image_name")
        if [ -n "$container_id" ]; then
            echo "Remove running container $container_id"
            docker container rm -f "$container_id"
        fi
        docker rmi -f "$image_name"
    fi
fi


cd "$( dirname "${BASH_SOURCE[0]}" )"

build_dir=$(mktemp -d -t docker-build-XXXXXX)
trap "rm -rf $build_dir" EXIT

echo "Using temporary build directory $build_dir"
cp -r ../benchmark $build_dir
cp Dockerfile $build_dir

echo "Building docker image"
docker build -t $image_name \
    -f "$build_dir/Dockerfile" "$build_dir"

echo "Done"