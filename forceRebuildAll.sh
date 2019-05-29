#!/usr/bin/env bash

docker-compose down
# remove existing data from database
sudo rm -rf /srv/docker/postgres
# if things wont work as intended try uncommenting the next line:
#docker-compose build --no-cache
docker-compose up -d --build --force-recreate
echo "IP's might have changed!"