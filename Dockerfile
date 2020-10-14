# pull official base image
FROM python:latest as base

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update

#debug 
FROM base as debug
RUN pip install ptvsd