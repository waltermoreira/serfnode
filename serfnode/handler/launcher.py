#!/usr/bin/env python
from __future__ import print_function

import functools
import json
import os
import signal
import socket
import sys
import time

import docker_utils
from file_utils import wait_for_files, atomic_write
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
        wait_for_files('/pos_{}'.format(pos))
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
        with atomic_write('/pos_{}'.format(pos+1)) as f:
            f.write(str(pos+1))
    return cid


def inject_child_info(cid):
    net_id = socket.gethostname()
    id = json.load(open('/me.json'))['id']
    inspect = docker_utils.client.inspect_container(cid)
    if net_id is not None:
        # Use network info from the first child from who we share the network
        net_parent = docker_utils.client.inspect_container(net_id)
        inspect['NetworkSettings'] = net_parent['NetworkSettings']
    info = {
        'id': id,
        'inspect': inspect
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
    # write child (cid) to known pipe
    wait_for_files('/tmp/children_server')
    with atomic_write('/tmp/children_server') as f:
        f.write(json.dumps(child) + '\n')
    wait_for_files('/me.json')
    inject_child_info(child)
    docker_utils.docker('wait', child)
