FROM python:3.6-alpine

env PROJECT_DIR /metric
env USER metric

RUN mkdir -p $PROJECT_DIR
RUN adduser -u 1010 -h /home/$USER -D -s /bin/sh $USER
WORKDIR $PROJECT_DIR

USER root
RUN pip install pipenv
RUN apk add --update build-base

USER $USER
ADD requirements.txt .
RUN pip install --user -r requirements.txt
ADD app $PROJECT_DIR/app

EXPOSE 8181

CMD PYTHONPATH=`pwd` SETTINGS_MODULE=app.conf.prod python3 -m app
