#!/bin/bash
set -o allexport

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..

if [ -e .env ]; then
	source .env
fi
echo $HJQUBESHIP_DOCKER_IMAGE_LOCAL

docker build -t $HJQUBESHIP_DOCKER_IMAGE_LOCAL:$HJQUBESHIP_IMAGE_VERSION . 
