#!/usr/bin/env bash

service nginx start

# run lets-encrypt only if we got apikey for cloudflare...
if [ -n "$CF_Account_ID" ] &  [ -n "$CF_HOSTNAME" ]; then
  sed -i -e 's/mesa.mosla.de/'"$CF_HOSTNAME"'/g' nginx_ssl.conf
  cp nginx_ssl.conf /etc/nginx/nginx.conf
  bash /root/.acme.sh/acme.sh --issue --dns dns_cf -d "$CF_HOSTNAME" --reloadcmd "service nginx force-reload"
fi
# -d mesa.mosla.de \
#--key-file       /path/to/keyfile/in/nginx/key.pem  \
#--fullchain-file /path/to/fullchain/nginx/cert.pem \

#source venv/bin/activate
uwsgi --ini uwsgi.ini --enable-threads
