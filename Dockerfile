FROM python:3.6-slim as builder
#FROM python:3.6-alpine
MAINTAINER Peter Michael Schwarz "peter.schwarz@uni-marburg.de"
# uwsgi-plugin-python3
COPY . /dna_sim
WORKDIR /dna_sim

RUN apt-get update -y \
 && apt-get install --no-install-recommends -y nginx build-essential wget cron swig ghostscript \
 && pip3 install -r requirements.txt --no-cache-dir \
 && wget -O -  https://get.acme.sh | sh \
 && mv nginx.conf /etc/nginx \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN tar -xvf RNAstructureSource.tgz \
 && cd RNAstructure \
 && sed -i 's/@# The wrapper is placed in the RNAstructure directory. Move it to exe\//mv ..\/_RNAstructure_wrap.cpython-36m-x86_64-linux-gnu.so ..\/$(WRAPPER_LIB_NAME)/g' RNAstructure_python_interface/Makefile \
 && make all && make python_setup \
 && cd .. \
 && rm RNA*.tgz \
 && apt-get purge -y --auto-remove swig build-essential


# COPY nginx.conf /etc/nginx

# RUN chmod +x ./start.sh
# CMD ["./start.sh"]
# ENTRYPOINT ["/bin/bash", "/dna_sim/start.sh"]
# CMD ["app.py"]

# squash / reduce size
FROM scratch
COPY --from=builder / /
WORKDIR /dna_sim

ENV PYTHONPATH "${PYTHONPATH}:/dna_sim/RNAstructure/exe"
ENV PATH "${PATH}:/dna_sim/RNAstructure/exe"
CMD export PATH
ENTRYPOINT ["/bin/bash", "/dna_sim/start.sh"]