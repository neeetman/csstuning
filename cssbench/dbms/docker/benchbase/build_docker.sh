#!/bin/bash
set -euo pipefail

image_name="dbms-benchmark:0.1"
cd "$(dirname "${BASH_SOURCE[0]}")"

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
        docker rmi "$image_name"
    fi
fi

build_dir=$(mktemp -d -t docker-build-XXXXXX)
trap "rm -rf $build_dir" EXIT

echo "Using temporary build directory $build_dir"
cp benchbase-mysql.tgz Dockerfile $build_dir

echo "Building docker image"
docker build -t $image_name \
    --build-arg CONTAINERUSER_UID=$(id -u) \
    --build-arg CONTAINERUSER_GID=$(id -g) \
    -f "$build_dir/Dockerfile" "$build_dir"

echo "Done"