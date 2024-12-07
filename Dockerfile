FROM python:3.12-alpine

WORKDIR /code
RUN apk add --no-cache gcc musl-dev linux-headers
COPY ./app/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./app/main.py main.py

EXPOSE 3000
