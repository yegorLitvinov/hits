FROM python:3.6-alpine

env PROJECT_DIR /metric
env USER metric

RUN mkdir -p $PROJECT_DIR
RUN adduser -u 1010 -h /home/$USER -D -s /bin/sh $USER
WORKDIR $PROJECT_DIR

USER root
RUN apk add --update build-base
RUN rm -rf /var/cache/apk/*

USER $USER
ADD requirements/prod.txt .
RUN pip install --user -r prod.txt
ADD app ./app

EXPOSE 8181

CMD PYTHONPATH=`pwd` SETTINGS_MODULE=app.conf.prod python3 -m app
