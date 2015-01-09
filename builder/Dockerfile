FROM ubuntu

RUN apt-get update -y && \
    apt-get install -y python python-pip && \
    pip install cookiecutter
COPY template/ /template
COPY entry.sh /entry.sh

WORKDIR /target
CMD ["/entry.sh"]
