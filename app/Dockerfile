FROM python:3.6
ENV USER metric
ENV PROJECT_DIR /home/$USER
RUN adduser --uid 1010 --home --disabled-password $PROJECT_DIR $USER

WORKDIR $PROJECT_DIR
ADD ./requirements/prod.txt ./
USER $USER
RUN pip install --no-cache-dir --user -r prod.txt

EXPOSE 8181
CMD /bin/sh ./app/entrypoint.sh
