#!/bin/bash

set -eu
scriptdir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
cd "$scriptdir/"

MYSQL_CONTAINER_NAME="mysql"
BENCHBASE_CONTAINER_NAME="benchbase"

function check_container_running {
    local name=$1
    if docker ps --filter "name=$name" | grep -q $name; then
        echo "Container $name is already running. Removing..."
        docker rm -f $name
    fi
}

function stop_and_remove_container {
    local name=$1
    if docker ps -a --filter "name=$name" | grep -q $name; then
        echo "Stopping and removing container $name..."
        docker stop $name
        docker rm $name
    fi
}

function start_mysql {
    echo "Starting mysql"
    docker run -d \
        --name $MYSQL_CONTAINER_NAME \
        -e MYSQL_ROOT_PASSWORD=password \
        -e MYSQL_USER=admin \
        -e MYSQL_PASSWORD=password \
        -e MYSQL_DATABASE=benchbase \
        -p 3306:3306 \
        -v $(pwd)/config/mysql/my.cnf:/etc/mysql/my.cnf \
        mysql:latest --max-connections=500
}

function start_benchbase {
    echo "Starting benchbase"
    docker run -d \
        --name $BENCHBASE_CONTAINER_NAME \
        --network="host" \
        -v $(pwd)/config/benchbase/mysql:/benchbase/mysql/config \
        dbms-benchmark:0.1 tail -f /dev/null
}

trap cleanup ERR

function cleanup {
    echo "Error occurred. Cleaning up containers..."
    stop_and_remove_container $MYSQL_CONTAINER_NAME
    stop_and_remove_container $BENCHBASE_CONTAINER_NAME
    exit 1
}

# Check if containers are already running
check_container_running $MYSQL_CONTAINER_NAME
check_container_running $BENCHBASE_CONTAINER_NAME

# Start containers
start_mysql
start_benchbase