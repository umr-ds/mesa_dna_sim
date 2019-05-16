FROM ubuntu:latest
MAINTAINER Peter Michael Schwarz "peter.schwarz@uni-marburg.de"
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential
COPY . /dna_sim
WORKDIR /dna_sim
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["app.py"]
