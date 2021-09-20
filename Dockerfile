FROM ubuntu:20.04

RUN apt-get update
RUN apt-get update && apt-get install -y \
    osmium-tool