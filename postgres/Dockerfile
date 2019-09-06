FROM postgres:alpine

COPY pg_dump.sql /docker-entrypoint-initdb.d/pg_dump.pg_sql
COPY init.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/init.sh