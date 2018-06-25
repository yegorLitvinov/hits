FROM python:3.6-alpine
ENV USER metric
ENV PROJECT_DIR /home/$USER
RUN mkdir -p $PROJECT_DIR
RUN adduser -u 1010 -h $PROJECT_DIR -D -s /bin/sh $USER

RUN apk add --update --no-cache build-base
WORKDIR $PROJECT_DIR
ADD ./requirements/prod.txt ./
USER $USER
RUN pip install --no-cache-dir --user -r prod.txt

EXPOSE 8181
CMD /bin/sh ./app/entrypoint.sh
