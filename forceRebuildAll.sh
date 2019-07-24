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
if [[ "$1" == "--clear-db" || "$1" == "-c" ]];
then
    sudo rm -rf /srv/docker/postgresql
    echo "!! REMOVING EXISTING DB !!"
fi

# if things wont work as intended try uncommenting the next line:
#docker-compose build --no-cache
docker-compose up -d --build --force-recreate
echo "IP's might have changed!"
