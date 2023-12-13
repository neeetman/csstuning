#!/bin/bash
set -euo pipefail

image_name="csstuning-dbms:0.1"
mysql_image="mysql:5.7"

echo "Building docker image $image_name"

skip_confirmation=false
if [ "$#" -gt 0 ] && [ "$1" = "-y" ]; then
    skip_confirmation=true
fi

if docker image inspect "$image_name" >/dev/null 2>&1; then
    echo "$image_name exists"
    if [ "$skip_confirmation" = true ]; then
        answer="y"
        echo "Automatically removing due to -y flag"
    else
        echo "Do you want to remove it? [Y/n]"
        read answer
    fi
    if [ "$answer" != "${answer#[Yy]}" ]; then
        container_id=$(docker ps -aq --filter "ancestor=$image_name")
        if [ -n "$container_id" ]; then
            echo "Remove running container $container_id"
            docker container rm -f "$container_id"
        fi
        docker rmi -f "$image_name"
    fi
fi

cd "$(dirname "${BASH_SOURCE[0]}")"

build_dir=$(mktemp -d -t docker-build-XXXXXX)
trap "rm -rf $build_dir" EXIT

echo "Using temporary build directory $build_dir"
cp -r ../benchmark $build_dir
cp Dockerfile $build_dir

echo "Building docker image"
docker build -t $image_name \
    --build-arg CONTAINERUSER_UID=$(id -u) \
    --build-arg CONTAINERUSER_GID=$(id -g) \
    -f "$build_dir/Dockerfile" "$build_dir"

# Pull mysql image
docker pull $mysql_image

echo "Done"