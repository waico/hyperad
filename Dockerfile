FROM python:3.10.0

WORKDIR /hyperad

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./src/requirements.txt /hyperad
RUN pip install -r requirements.txt

COPY ./src /hyperad
