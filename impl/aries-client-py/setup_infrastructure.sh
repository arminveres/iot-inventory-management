#!/bin/env bash
set -e
set -o pipefail

# ./scripts/cryptoGen.sh

./scripts/run_postgres

../dependencies/von-network/manage start
../dependencies/indy-tails-server/docker/manage start

docker run -it --rm -v "$(pwd)"/crypto/:/etc/orion-server/crypto -p 6001:6001 \
    -p 7050:7050 orionbcdb/orion-server
