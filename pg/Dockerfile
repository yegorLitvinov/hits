FROM postgres:9.6-alpine

ENV ENTRYPOINT_DIR /docker-entrypoint-initdb.d
RUN mkdir -p $ENTRYPOINT_DIR
WORKDIR $ENTRYPOINT_DIR

ADD init.sql ./
