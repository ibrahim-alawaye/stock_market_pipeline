#!/bin/sh

HOST_IP=$(ip route | awk '/default/ { print $3 }')

echo "$HOST_IP host.docker.internal" >> /etc/hosts

exec "$@"
