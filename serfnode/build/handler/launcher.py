#!/usr/bin/env python

import functools
import json
import os
import signal
import socket
import sys

import docker_utils
from info import NODE_INFO


def handler(name, signum, frame):
    print('Should kill', name)
    try:
        cid = open('/child_{}'.format(name)).read().strip()
        docker_utils.client.remove_container(cid, force=True)
    except Exception:
        pass
    sys.exit(0)


def launch(name, args):
    try:
        cid = open('/child_{}'.format(name)).read().strip()
    except IOError:
        cid = name
    try:
        os.unlink('/child_{}'.format(name))
    except OSError:
        pass
    try:
        docker_utils.client.remove_container(cid, force=True)
    except Exception:
        pass
    args.insert(0, '--cidfile=/child_{}'.format(name))
    docker_utils.docker('run',
                        '--volumes-from={}'.format(socket.gethostname()),
                        *args)


def inject_ip():
    with open('/serfnode/parent_info', 'w') as parent_info:
        json.dump(NODE_INFO, parent_info)


def wait(name):
    cid = open('/child_{}'.format(name)).read().strip()
    docker_utils.docker('wait', cid)


if __name__ == '__main__':
    name = sys.argv[1]
    args = sys.argv[2:]
    signal.signal(signal.SIGINT, functools.partial(handler, name))
    inject_ip()
    launch(name, args)
