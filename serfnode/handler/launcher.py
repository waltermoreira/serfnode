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
    net_id = None
    if pos is not None and pos > 0:
        # wait for file /pos_{pos}
        while not os.path.exists('/pos_{}'.format(pos)):
            time.sleep(0.1)
        # grab cid of a previously started child
        net_id = open('/tmp/network').read()
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
    if net_id is not None:
        args.insert(0, '--net=container:{}'.format(net_id))
    cid = docker_utils.docker(
        'run', '-d',
        '--volumes-from={}'.format(socket.gethostname()),
        *args)
    if pos is not None:
        # touch file /pos_{pos+1}
        with open('/pos_{}'.format(pos+1), 'w') as f:
            pass
    with open('/tmp/network', 'w') as f:
        f.write(cid)
    return cid


def inject_child_info(cid):
    id = json.load(open('/me.json'))['id']
    info = {
        'id': id,
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
    # write child (cid) to known pipe
    while not os.path.exists('/tmp/children_server'):
        time.sleep(0.1)
    with open('/tmp/children_server', 'w') as f:
        f.write(json.dumps(child) + '\n')
    while True:
        try:
            json.load(open('/me.json'))
            break
        except (ValueError, IOError):
            time.sleep(0.1)
            continue
    inject_child_info(child)
    docker_utils.docker('wait', child)
