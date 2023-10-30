#!/bin/bash

set -eu
scriptdir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
cd "$scriptdir/"

MYSQL_CONTAINER_NAME="mysql"
BENCHBASE_CONTAINER_NAME="benchbase"

function stop_and_remove_container {
    local name=$1
    if docker ps -a --filter "name=$name" | grep -q $name; then
        echo "Stopping and removing container $name..."
        docker stop $name
        docker rm $name
    else
        echo "Container $name is not running or does not exist."
    fi
}

# Stop and remove containers
stop_and_remove_container $MYSQL_CONTAINER_NAME
stop_and_remove_container $BENCHBASE_CONTAINER_NAME

echo "Containers stopped and removed successfully."