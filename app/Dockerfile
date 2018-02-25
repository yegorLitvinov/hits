FROM python:3.6-alpine

env PROJECT_DIR /metric
env USER metric

RUN apk add --update build-base
RUN rm -rf /var/cache/apk/*

RUN mkdir -p $PROJECT_DIR
RUN adduser -u 1010 -h /home/$USER -D -s /bin/sh $USER

WORKDIR $PROJECT_DIR
ADD ./ ./app
RUN chown -R metric:metric /metric/

USER $USER
RUN pip install --user -r app/requirements/prod.txt
EXPOSE 8181

CMD /bin/sh ./app/entrypoint.sh
