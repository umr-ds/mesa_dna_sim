#!/usr/bin/env bash

if [[ ! -f /var/lib/postgresql/data/db_initialized.lock ]]; then
    cat /docker-entrypoint-initdb.d/pg_dump.pg_sql | psql -U postgres
    touch /var/lib/postgresql/data/db_initialized.lock
else
    echo "IGNORING pg_dump since db_initialized.lock exists"
fi
