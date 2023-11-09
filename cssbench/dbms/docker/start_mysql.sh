#!/bin/bash

set -eu

MYSQL_IMAGE_NAME="mysql:5.7"
MYSQL_CONTAINER_NAME="csstuning_mysql"
CONTAINERUSER_GID=$(id -g)
CONTAINERUSER_UID=$(id -u)

# Default values if not provided by arguments
MYSQL_CONFIG_FILE=""
MYSQL_DATA_DIR="$HOME/.csstuning/dbms/mysql_data"
HOST_PORT=3307
NUM_CPUS="8.0"
MEM_SIZE="16g"

while [[ "$#" -gt 0 ]]; do
    case $1 in
    --config-file)
        MYSQL_CONFIG_FILE=$(readlink -f "$2")
        shift
        ;;
    --cpus)
        NUM_CPUS="$2"
        shift
        ;;
    --memory)
        MEM_SIZE="$2"
        shift
        ;;
    *)
        echo "Usage: $0 [--config-file <path>] [--cpus <number>] [--memory <size>]"
        exit 1
        ;;
    esac
    shift
done

# Check if MYSQL_DATA_DIR exists, if not create it
if [[ ! -d "$MYSQL_DATA_DIR" ]]; then
    echo "Create MySQL data directory $MYSQL_DATA_DIR"
    mkdir -p "$MYSQL_DATA_DIR"
fi

function check_container_running {
    local name=$1
    if docker ps -a --filter "name=$name" | grep -q $name; then
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
    echo "Starting MySQL container with name: $MYSQL_CONTAINER_NAME"

    # Assemble the Docker run command
    local docker_run_command=(
        docker run -d
        --name $MYSQL_CONTAINER_NAME
        -e MYSQL_ROOT_PASSWORD=password
        -e MYSQL_USER=admin
        -e MYSQL_PASSWORD=password
        -e MYSQL_DATABASE=benchbase
        -p $HOST_PORT:3306
        --user "$CONTAINERUSER_UID:$CONTAINERUSER_GID"
        -v "$MYSQL_DATA_DIR:/var/lib/mysql"
        --cpus=$NUM_CPUS
        --memory=$MEM_SIZE
    )

    # Add the MySQL config file mount if specified
    if [[ -n $MYSQL_CONFIG_FILE && -f $MYSQL_CONFIG_FILE ]]; then
        docker_run_command+=(
            -v "$MYSQL_CONFIG_FILE:/etc/mysql/conf.d/custom.cnf"
            $MYSQL_IMAGE_NAME
        )
    else
        docker_run_command+=(
            $MYSQL_IMAGE_NAME
        )
    fi

    "${docker_run_command[@]}"
}

trap cleanup ERR

function cleanup {
    echo "Error occurred. Cleaning up container..."
    stop_and_remove_container $MYSQL_CONTAINER_NAME
    exit 1
}

scriptdir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
cd "$scriptdir/"

# Check if MySQL configuration file is present and valid
if [[ -n $MYSQL_CONFIG_FILE && ! -f $MYSQL_CONFIG_FILE ]]; then
    echo "MySQL configuration file is missing."
    exit 1
fi

# Check if MySQL container is already running
check_container_running $MYSQL_CONTAINER_NAME

# Start MySQL container
start_mysql
