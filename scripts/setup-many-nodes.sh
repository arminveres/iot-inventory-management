#!/usr/bin/env bash
set -e

NUMBER_NODES=$1
START_PORT=8100
END_PORT=$((START_PORT + NUMBER_NODES * 10))
NAME_PREFIX="controller_node_"

mkdir -p logs .agent_cache
for ((i = START_PORT; i < END_PORT; i += 10)); do
	(
		echo "Running node: $i"
		./run --background --type node --port $i --name "$NAME_PREFIX$i" &>./logs/"$NAME_PREFIX$1"
	) &
done
