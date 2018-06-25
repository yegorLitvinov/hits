FROM python:3.6
ENV USER metric
ENV PROJECT_DIR /home/$USER
RUN adduser --uid 1010 --home $PROJECT_DIR --disabled-password $USER

WORKDIR $PROJECT_DIR
ADD --chown=metric:metric ./ ./app/
USER $USER
RUN pip install --no-cache-dir --user -r ./app/requirements/prod.txt

EXPOSE 8181
CMD /bin/sh ./app/entrypoint.sh
