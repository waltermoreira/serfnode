#!/usr/bin/env python

import json
import time
import os
import socket

import pipe
from join import get_info
import docker_utils
from file_utils import wait_for_file, atomic_write


def handler(obj):
    try:
        old = json.load(open('/children_by_name.json'))
    except IOError:
        old = {}
    wait_for_file('/agent_up')
    new = get_info(obj)
    parent = docker_utils.client.inspect_container(socket.gethostname())
    new['inspect']['NetworkSettings'] = parent['NetworkSettings']
    name = new['inspect']['Name'][1:]
    old[name] = new
    with atomic_write('/children_by_name.json') as f:
        json.dump(old, f)


if __name__ == '__main__':
    pipe.server('/tmp/children_server', handler)
