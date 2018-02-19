FROM postgres:9.6-alpine

ENV ENTRYPOINT_DIR /docker-entrypoint-initdb.d
RUN mkdir -p $ENTRYPOINT_DIR
WORKDIR $ENTRYPOINT_DIR

# Anyway, you need to run schema.sql manually
# because of volume (of course if you use one).
ADD init_prod.sql schema.sql ./
