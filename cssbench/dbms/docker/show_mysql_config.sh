#!/bin/bash

CONTAINER_NAME_OR_ID="csstuning_mysql"
MYSQL_ROOT_PASSWORD="password"

docker exec $CONTAINER_NAME_OR_ID mysql -u root -p$MYSQL_ROOT_PASSWORD -e 'SHOW GLOBAL VARIABLES;'
