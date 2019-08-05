FROM python:3.6-slim as builder
#FROM python:3.6-alpine
MAINTAINER Peter Michael Schwarz "peter.schwarz@uni-marburg.de"
# uwsgi-plugin-python3
COPY . /dna_sim
WORKDIR /dna_sim

RUN apt-get update -y \
 && apt-get install --no-install-recommends -y nginx build-essential wget cron \
 && pip3 install -r requirements.txt --no-cache-dir \
 && apt-get purge -y --auto-remove build-essential \
 && wget -O -  https://get.acme.sh | sh \
 && mv nginx.conf /etc/nginx \
 && mv nginx_ssl.conf /etc/nginx \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# COPY nginx.conf /etc/nginx

# RUN chmod +x ./start.sh
# CMD ["./start.sh"]
# ENTRYPOINT ["/bin/bash", "/dna_sim/start.sh"]
# CMD ["app.py"]

# squash / reduce size
FROM scratch
COPY --from=builder / /
WORKDIR /dna_sim
ENTRYPOINT ["/bin/bash", "/dna_sim/start.sh"]