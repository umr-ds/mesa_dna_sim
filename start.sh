#!/usr/bin/env bash

service nginx start

# run lets-encrypt only if we got apikey for cloudflare...
if [ -n "$CF_Account_ID" ]; then
  mv nginx_ssl.conf nginx.conf
  bash /root/.acme.sh/acme.sh --issue --dns dns_cf -d mosla.peter-michael-schwarz.de -d peter-michael-schwarz.de \
    --reloadcmd "service nginx force-reload"
fi
# -d www.peter-michael-schwarz.de \
#--key-file       /path/to/keyfile/in/nginx/key.pem  \
#--fullchain-file /path/to/fullchain/nginx/cert.pem \

#source venv/bin/activate
uwsgi --ini uwsgi.ini --enable-threads
