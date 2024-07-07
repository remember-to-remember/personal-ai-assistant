#!/usr/bin/env bash
set -euxo pipefail

# Get the directory where the script is located
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p $script_dir/certs
if [ -d "/etc/letsencrypt/live/api.remember2.co" ]; then
    mkdir -p $script_dir/certs/api.remember2.co
    cp /etc/letsencrypt/live/api.remember2.co/fullchain.pem $script_dir/certs/api.remember2.co/fullchain.pem
    cp /etc/letsencrypt/live/api.remember2.co/privkey.pem $script_dir/certs/api.remember2.co/privkey.pem
fi
if [ -d "/etc/letsencrypt/live/app.remember2.co" ]; then
    mkdir -p $script_dir/certs/app.remember2.co
    cp /etc/letsencrypt/live/app.remember2.co/fullchain.pem $script_dir/certs/app.remember2.co/fullchain.pem
    cp /etc/letsencrypt/live/app.remember2.co/privkey.pem $script_dir/certs/app.remember2.co/privkey.pem
fi

# change ownership to local user
chown $1 certs certs/**/**
