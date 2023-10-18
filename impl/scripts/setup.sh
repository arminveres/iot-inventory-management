#!/bin/env bash
set -e
set -o pipefail

# on Windows, docker run needs to be prefixed by winpty
if [ "$OSTYPE" == "msys" ]; then
    DOCKER="winpty docker"
else
    DOCKER=${DOCKER:-docker}
fi

$DOCKER run --rm -ti --name indy-demo-postgres \
    -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 \
    -d postgres:11 \
    -c 'log_statement=all' -c 'logging_collector=on' -c 'log_destination=stderr' \
    -c 'log_connections=on'

echo "Running from Directory:  $(pwd)"

"$(pwd)"/dependencies/von-network/manage start
"$(pwd)"/dependencies/indy-tails-server/docker/manage start

$DOCKER run -dit \
    --rm \
    --name oriondb \
    -v "$(pwd)"/crypto/:/etc/orion-server/crypto \
    -p 6001:6001 \
    -p 7050:7050 \
    orionbcdb/orion-server
