#!/usr/bin/env bash
set -e

NAME_PREFIX="controller_node_"
DOCKER_CONTAINERS=$(docker container ls --format '{{.ID}} {{.Names}}' | grep $NAME_PREFIX)

while read -r line; do
	(
		CONTAINER_ID=$(echo "$line" | awk '{print $1}')
		CONTAINER_NAME=$(echo "$line" | awk '{print $2}')
		echo "Stopping $CONTAINER_NAME ..."
		docker container stop "$CONTAINER_ID" &>/dev/null
	) &
done <<<"$DOCKER_CONTAINERS"

rm -f ./.agent_cache/mass_onboarding
