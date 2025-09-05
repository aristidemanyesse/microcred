# Utilisation de l'image officielle de Python
FROM python:3.10-slim

RUN apt-get update && apt-get install -y cron nano && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/requirements.txt

RUN pip3 install -r /code/requirements.txt

COPY ./source /code/source
COPY ./start.sh /code/start.sh

WORKDIR /code/source
EXPOSE 8000

USER root
RUN chmod +x /code/start.sh

ENTRYPOINT ["/code/start.sh"]
