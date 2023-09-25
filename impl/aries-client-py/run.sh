#!/bin/env bash
set -e

DOCKERHOST=$(./scripts/getDockerHost.sh)
LEDGER_URL="http://$DOCKERHOST:9000"
GENESIS_URL="$LEDGER_URL/genesis"
RUN_MODE="docker"
DOCKER_NETWORK="bridge" # bridge or host

agent_name=$1
port=$2
# We define a portrange of +9 for each agent
portrange="$2-$((port + 9))"

docker build -t aries-my-agent . || exit 1
docker container run --rm -it \
    --network="$DOCKER_NETWORK" \
    -p 0.0.0.0:"$portrange":"$portrange" \
    -e LEDGER_URL="$LEDGER_URL" \
    -e GENESIS_URL="$GENESIS_URL" \
    -e RUNMODE="$RUN_MODE" \
    -e DOCKERHOST="$DOCKERHOST" \
    -e POSTGRES=1 \
    aries-my-agent "$agent_name" \
    --wallet-type askar \
    --port "$port" \
    --did-exchange \
    --reuse-connections
