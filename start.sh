#!/usr/bin/env bash
service nginx start
#source venv/bin/activate
uwsgi --ini uwsgi.ini --enable-threads
