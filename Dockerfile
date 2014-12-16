FROM ubuntu:14.04

MAINTAINER Walter Moreira <wmoreira@tacc.utexas.edu>

RUN apt-get update -y && \
    apt-get install -y python python-dev python-pip supervisor git
RUN apt-get install -y libzmq-dev
RUN pip install serf_master fig jinja2 ipython
WORKDIR /tmp
RUN echo 2
RUN git clone https://github.com/waltermoreira/mischief.git
WORKDIR /tmp/mischief
RUN python setup.py install

WORKDIR /
COPY serf /usr/bin/
COPY handler /handler
COPY serfnode.conf /etc/supervisor/conf.d/
COPY programs /programs

EXPOSE 7946 7373

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
