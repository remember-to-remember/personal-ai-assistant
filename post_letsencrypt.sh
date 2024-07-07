#!/usr/bin/env bash
set -euxo pipefail

# Get the directory where the script is located
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p $script_dir/certs
cp /etc/letsencrypt/live/api.remember2.co/fullchain.pem $script_dir/certs/fullchain.pem
cp /etc/letsencrypt/live/api.remember2.co/privkey.pem $script_dir/certs/privkey.pem

# change ownership to local user
chown $1 certs certs/*
