FROM python:3.6-slim
#FROM python:3.6-alpine
MAINTAINER Peter Michael Schwarz "peter.schwarz@uni-marburg.de"
#RUN apk update
RUN apt-get update -y
#RUN apk add nginx
#RUN apk add uwsgi-python3
#RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev
RUN apt-get install -y nginx python3-pip python3-dev build-essential uwsgi-plugin-python3
COPY . /dna_sim
WORKDIR /dna_sim
 
#RUN pip3 install --upgrade pip==18.1 &&\
RUN pip3 install -r requirements.txt
#&& apk del .build-deps
#ENTRYPOINT ["python3"]
COPY nginx.conf /etc/nginx
RUN chmod +x ./start.sh
CMD ["./start.sh"]
#CMD ["app.py"]
