# syntax=docker/dockerfile:1

## Note: best-practice for comments in a Dockerfile is _not_ to have them inline with commands.

## specifies base-image; Docker will pull this image from Docker Hub if it's not already locally available
FROM python:3.8

## prevents python from writing pyc files to disc (was in tutorial)
ENV PYTHONDONTWRITEBYTECODE=1  

## prevents python from buffering stdout and stderr (forces it to print everything immediately) (was in tutorial)
ENV PYTHONUNBUFFERED=1

## sets the working directory inside your container 
##  - if it doesn't exist, Docker will create it. 
##  - all RUN commands that follow will be run from this directory.
WORKDIR /container_project_stuff/ocra_lookup_project

## creates a 'logs' directory within the container
RUN mkdir /container_project_stuff/logs

## creates an 'example_data_source' directory within the container
RUN mkdir /container_project_stuff/example_data_source

## copies the contents of the current host directory (django_template_42_project) into the container at /container_project_stuff/ocra_lookup_project
COPY . /container_project_stuff/ocra_lookup_project/

## runs the pip install command inside the container
RUN pip install -r ./config/requirements_localdev.txt 
