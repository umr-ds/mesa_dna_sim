#!/usr/bin/env bash
if [[ "$1" == "--help" || "$1" == "-h" ]];
then
    echo ""
    echo "  Usage: $0 [ --clear-db | -c ]"
    echo ""
    echo ""
    echo "  Options:"
    echo ""
    echo "    -c, --clear-db               clears the existing Database and forces a reload from the provided Dump"
    exit 0
fi

docker-compose down
./buildBulma.sh


# remove existing data from database
if [[ "$1" == "--clear-db" || "$1" == "-c" || "$2" == "--clear-db" || "$2" == "-c" ]];
then
    echo "!! REMOVING EXISTING DB !!"
    sudo rm -rf /srv/docker/postgresql
    sudo rm -rf /srv/docker/redis
fi

if [[ "$1" == "--no-cache" || "$1" == "-n" || "$2" == "--no-cache" || "$2" == "-n" ]];
then
    echo "!! IGNORING CACHE - THIS WILL TAKE LONGER !!"
    docker-compose build --no-cache
else
    docker-compose build
fi

# if things wont work as intended try uncommenting the next line:
docker-compose up -d  # --build --force-recreate
echo "IP's might have changed!"
