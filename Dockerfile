FROM python:3.6-alpine

env PROJECT_DIR /app
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
ADD app/ $PROJECT_DIR

EXPOSE 8181

ENTRYPOINT ["/bin/sh"]
# ENTRYPOINT ["python -m app"]
# CMD ["ls", "-lah"]
# CMD ["python3", "-m app"]
