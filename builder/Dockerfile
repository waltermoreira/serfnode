FROM ubuntu

RUN apt-get update -y && \
    apt-get install -y python python-pip && \
    pip install cookiecutter
COPY template/ /template

WORKDIR /data
CMD ["cookiecutter", "/template"]
