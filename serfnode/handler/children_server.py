#!/usr/bin/env python

import json
import time
import os
import socket

import pipe
from join import get_info
import docker_utils


def handler(obj):
    try:
        old = json.load(open('/children_by_name.json'))
    except IOError:
        old = {}
    while not os.path.exists('/agent_up'):
        time.sleep(0.1)
    new = get_info(obj)
    parent = docker_utils.client.inspect_container(socket.gethostname())
    new['inspect']['NetworkSettings'] = parent['NetworkSettings']
    name = new['inspect']['Name'][1:]
    old[name] = new
    with open('/children_by_name.json', 'w') as f:
        json.dump(old, f)


if __name__ == '__main__':
    pipe.server('/tmp/children_server', handler)
