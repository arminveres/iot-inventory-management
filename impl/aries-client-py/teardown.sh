#!/bin/env bash
set -e
set -o pipefail

# on Windows, docker run needs to be prefixed by winpty
if [ "$OSTYPE" == "msys" ]; then
    DOCKER="winpty docker"
else
    DOCKER=${DOCKER:-docker}
fi

$DOCKER stop indy-demo-postgres &>/dev/null &&
echo "Stopped previous postgres container" || true

../dependencies/von-network/manage down
../dependencies/indy-tails-server/docker/manage down

$DOCKER container stop oriondb
