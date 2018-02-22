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
ADD ./ ./app
RUN pip install --user -r app/requirements/prod.txt
ADD entrypoint.sh ./

EXPOSE 8181

CMD /bin/sh ./entrypoint.sh
