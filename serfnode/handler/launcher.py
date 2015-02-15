#!/usr/bin/env python

import functools
import json
import os
import signal
import socket
import sys
import time

import docker_utils
import serf


def handler(name, signum, frame):
    print('Should kill', name)
    try:
        cid = open('/child_{}'.format(name)).read().strip()
        docker_utils.client.kill(cid)
    except Exception:
        pass
    sys.exit(0)


def launch(name, args, pos=None):
    if pos is not None and pos > 0:
        # wait for file /pos_{pos}
        while not os.path.exists('/pos_{}'.format(pos)):
            time.sleep(0.1)
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
    cid = docker_utils.docker(
        'run', '-d',
        '--volumes-from={}'.format(socket.gethostname()),
        *args)
    if pos is not None:
        # touch file /pos_{pos+1}
        with open('/pos_{}'.format(pos+1), 'w') as f:
            pass
    return cid


def inject_child_info(cid):
    info = {
        'id': serf.serf_json('info')['agent']['name'],
        'inspect': docker_utils.client.inspect_container(cid)
    }
    docker_utils.docker(
        'exec', cid, 'bash', '-c',
        "echo '{}' > /me.json".format(json.dumps(info)))


def wait(name):
    cid = open('/child_{}'.format(name)).read().strip()
    docker_utils.docker('wait', cid)


if __name__ == '__main__':
    pos = None
    name = sys.argv[1]
    if name.startswith('--pos'):
        pos = int(name[6:])
        del sys.argv[1]
        name = sys.argv[1]
    args = sys.argv[2:]
    signal.signal(signal.SIGINT, functools.partial(handler, name))
    child = launch(name, args, pos=pos)
    inject_child_info(child)
    docker_utils.docker('wait', child)
