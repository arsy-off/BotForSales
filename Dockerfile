FROM python:3.11.2-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2
RUN pip install -r requirements.txt

COPY bot bot
COPY main.py main.py

CMD ["python3", "main.py"]

