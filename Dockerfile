FROM python:3.6-slim
MAINTAINER Peter Michael Schwarz "peter.schwarz@uni-marburg.de"
RUN apt-get update -y
RUN apt-get install -y nginx python3-pip python3-dev build-essential uwsgi-plugin-python3
COPY . /dna_sim
WORKDIR /dna_sim
RUN pip3 install -r requirements.txt
#ENTRYPOINT ["python3"]
COPY nginx.conf /etc/nginx
RUN chmod +x ./start.sh
CMD ["./start.sh"]
#CMD ["app.py"]
