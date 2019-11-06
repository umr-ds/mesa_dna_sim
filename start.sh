#!/usr/bin/env bash

service nginx start

# run lets-encrypt only if we got apikey for cloudflare...
if [ -n "$CF_Account_ID" ] &  [ -n "$CF_HOSTNAME" ]; then
  sed -i -e 's/mesa.mosla.de/'"$CF_HOSTNAME"'/g' nginx_ssl.conf
  cp nginx_ssl.conf /etc/nginx/nginx.conf
  bash /root/.acme.sh/acme.sh --issue --dns dns_cf -d "$CF_HOSTNAME" --reloadcmd "service nginx force-reload"
elif [ -n "$SELF_SIGNED_HOSTNAME" ];  then
 sed -i -e 's/mesa.mosla.de/'"$SELF_SIGNED_HOSTNAME"'/g' nginx_ssl.conf
 cp nginx_ssl.conf /etc/nginx/nginx.conf
 mkdir /root/.acme.sh/"$SELF_SIGNED_HOSTNAME"
 openssl req -newkey rsa:2048 -nodes -keyout /root/.acme.sh/"$SELF_SIGNED_HOSTNAME"/"$SELF_SIGNED_HOSTNAME".key -x509 -days 3650 -out /root/.acme.sh/"$SELF_SIGNED_HOSTNAME"/"$SELF_SIGNED_HOSTNAME".cer -subj "/C=DE/ST=Hessen/L=Marburg/O=MOSLA/CN=$SELF_SIGNED_HOSTNAME"
 sed -i -e 's/ssl_stapling on;//g' nginx_ssl.conf
 sed -i -e 's/ssl_stapling_verify on;//g' nginx_ssl.conf
 service nginx reload
fi
# -d mesa.mosla.de \
#--key-file       /path/to/keyfile/in/nginx/key.pem  \
#--fullchain-file /path/to/fullchain/nginx/cert.pem \

#source venv/bin/activate
uwsgi --ini uwsgi.ini --enable-threads
