FROM python:3.8

WORKDIR /home/urlspec

RUN apt update && \
    apt install -y redis

COPY . .

RUN python3 -m pip install -r requirements.txt

CMD service redis-server start && /bin/bash -c "bash runserver.sh"
