#!/usr/bin/env python

import functools
import json
import os
import signal
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
    docker_utils.docker('run', '-d', *args)


def inject_ip(name):
    cid = open('/child_{}'.format(name)).read().strip()
    content = json.dumps(NODE_INFO)
    docker_utils.docker('exec', cid,
                        'bash', '-c',
                        "echo '{}' > /parent_info".format(content))


def wait(name):
    cid = open('/child_{}'.format(name)).read().strip()
    docker_utils.docker('wait', cid)


if __name__ == '__main__':
    name = sys.argv[1]
    args = sys.argv[2:]
    signal.signal(signal.SIGINT, functools.partial(handler, name))
    launch(name, args)
    inject_ip(name)
    wait(name)
