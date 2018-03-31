FROM python:3.6-alpine AS builder
ENV USER metric
ENV PROJECT_DIR /home/$USER
RUN apk add --update --no-cache build-base
RUN mkdir -p $PROJECT_DIR
RUN adduser -u 1010 -h $PROJECT_DIR -D -s /bin/sh $USER
WORKDIR $PROJECT_DIR
ADD ./requirements/prod.txt ./
USER $USER
RUN pip install --no-cache-dir --user -r prod.txt

FROM python:3.6-alpine
ENV USER metric
ENV PROJECT_DIR /home/$USER
RUN mkdir -p $PROJECT_DIR
RUN adduser -u 1010 -h $PROJECT_DIR -D -s /bin/sh $USER
WORKDIR $PROJECT_DIR
# Can't use $USER env var here :(
COPY --chown=metric:metric --from=builder $PROJECT_DIR $PROJECT_DIR
ADD --chown=metric:metric ./ ./app
USER $USER
EXPOSE 8181
CMD /bin/sh ./app/entrypoint.sh
