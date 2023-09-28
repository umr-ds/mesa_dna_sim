FROM python:3.11-slim as builder
MAINTAINER Peter Michael Schwarz "peter.schwarz@uni-marburg.de"
COPY . /dna_sim
WORKDIR /dna_sim

RUN apt-get update -y \
 && apt-get install --no-install-recommends -y nginx build-essential wget cron swig ghostscript libssl-dev libffi-dev python-dev-is-python3 \
 && pip3 install -r requirements.txt --no-cache-dir \
 && wget -O -  https://get.acme.sh | sh \
 && mv nginx.conf /etc/nginx \
#RUN tar -xvf RNAstructureSourceLinuxTextInterfaces64bit.tgz \
 && tar -xvf RNAstructureSource.tgz \
 && cd RNAstructure \
 && sed -i 's/@# The wrapper is placed in the RNAstructure directory. Move it to exe\//mv ..\/_RNAstructure_wrap.cpython-38-x86_64-linux-gnu.so ..\/$(WRAPPER_LIB_NAME)/g' python_interface/Makefile \
 && sed -i 's/#include <map>/#include <string>\n#include <map>/g' CycleFold/constants.h \
 && make all && make python-interface PYTHON=python3 \
 && cd .. \
 && rm RNA*.tgz \
 && apt-get purge -y --auto-remove swig build-essential libssl-dev libffi-dev python-dev \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# squash / reduce size
FROM scratch
COPY --from=builder / /
WORKDIR /dna_sim

ENV PYTHONPATH "${PYTHONPATH}:/dna_sim/RNAstructure/exe"
ENV PATH "${PATH}:/dna_sim/RNAstructure/exe"
CMD export PATH
ENTRYPOINT ["/bin/bash", "/dna_sim/start.sh"]