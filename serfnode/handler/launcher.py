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
        docker_utils.client.kill(cid)
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
        # first try to start the container, if it exists
        docker_utils.client.start(cid)
        return cid
    except docker_utils.dockerpy.errors.APIError:
        pass
    # if start fails, just do a 'run'
    args.insert(0, '--cidfile=/child_{}'.format(name))
    return docker_utils.docker(
        'run', '-d',
        '--volumes-from={}'.format(socket.gethostname()),
        *args)


def inject_ip():
    with open('/serfnode/parent_info', 'w') as parent_info:
        json.dump(NODE_INFO, parent_info)


def inject_parent_info():
    with open('/serfnode/parent.json', 'w') as f:
        info = json.loads(
            docker_utils.docker('inspect', socket.gethostname()))
        json.dump(info[0], f)


def inject_child_info(cid):
    info = json.loads(docker_utils.docker('inspect', cid))
    docker_utils.docker(
        'exec', cid, 'bash', '-c',
        "echo '{}' > /me.json".format(json.dumps(info[0])))


def wait(name):
    cid = open('/child_{}'.format(name)).read().strip()
    docker_utils.docker('wait', cid)


if __name__ == '__main__':
    name = sys.argv[1]
    args = sys.argv[2:]
    signal.signal(signal.SIGINT, functools.partial(handler, name))
    inject_ip()
    inject_parent_info()
    child = launch(name, args)
    inject_child_info(child)
    docker_utils.docker('wait', child)
