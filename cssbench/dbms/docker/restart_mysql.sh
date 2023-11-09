#!/bin/bash

set -eu

MYSQL_CONTAINER_NAME="csstuning_mysql"

if docker ps -a --filter "name=$MYSQL_CONTAINER_NAME" | grep -q $MYSQL_CONTAINER_NAME; then
    docker restart $MYSQL_CONTAINER_NAME
else
    echo "Container $name is not running. Start it first."
    exit 1
fi
