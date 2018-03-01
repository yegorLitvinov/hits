FROM python:3.6-alpine

RUN apk add --update build-base
RUN rm -rf /var/cache/apk/*

env USER metric
env PROJECT_DIR /home/$USER

RUN mkdir -p $PROJECT_DIR
RUN adduser -u 1010 -h $PROJECT_DIR -D -s /bin/sh $USER
WORKDIR $PROJECT_DIR

ADD ./requirements/prod.txt ./
# this will be cached until requirements will be changed
RUN pip install -r prod.txt
ADD ./ ./app
RUN chown -R $USER:$USER $PROJECT_DIR
USER $USER

EXPOSE 8181
CMD /bin/sh ./app/entrypoint.sh
