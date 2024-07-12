#!/usr/bin/env bash
set -e

function get_zerotier_address {
	if [[ $# -gt 1 ]]; then
		echo "Only 1 argument allowed; the network name"
		exit 1
	fi
	network=$1

	printf "The usage of ZeroTier requires root privileges.\n"
	printf "The user may now be asked for the root password: \n\n"

	sudo zerotier-cli listnetworks | grep "$network" | awk '{print $9}' | sed 's/\/[0-9]*//g'
}

get_zerotier_address "$1"
