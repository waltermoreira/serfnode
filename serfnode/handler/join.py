#!/usr/bin/env python
"""
Launch a serf node.

The role of the node is retrieved from the environment variable ``ROLE``.

The node will join a cluster, if the ``CONTACT`` variable specifies an
address.

"""

import subprocess
import time
import multiprocessing
import json
import socket

import serf
from utils import get_ports, encode_ports
import config
import docker_utils
from handler import MyHandler
from file_utils import wait_for_files, atomic_write


def async_hook():
    p = multiprocessing.Process(target=hook)
    p.start()


def hook():
    wait_for_files('/agent_up', '/children_by_name.json')
    MyHandler.init()


def get_info(cid):
    sid = serf.serf_json('info')['agent']['name']
    inspect = docker_utils.client.inspect_container(cid)
    return {'id': sid, 'inspect': inspect}


def save_me(loc):
    with atomic_write(loc) as f:
        json.dump(get_info(socket.gethostname()), f)


def save_info():
    wait_for_files('/agent_up')
    save_me('/me.json')
    save_me('/serfnode/parent.json')


def async_save_info():
    p = multiprocessing.Process(target=save_info)
    p.start()


def main():
    role = config.role
    cmd = ('serf agent -event-handler=/handler/handler.py '
           '-log-level=debug -tag'
           .format(**locals()).split())
    cmd.append('role={role}'.format(**locals()))

    contact = config.peer
    if contact:
        cmd.extend(['-join', contact])

    ip = config.ip
    bind_port = config.bind_port

    cmd.extend(['-advertise', '{}:{}'.format(ip, bind_port)])
    cmd.extend(['-tag', 'ip={}'.format(ip),
                '-tag', 'serf_port={}'.format(bind_port)])
    cmd.extend(['-bind', '0.0.0.0:{}'.format(bind_port)])

    node = config.node
    cmd.extend(['-node', node])

    rpc_port = config.rpc_port
    cmd.extend(['-rpc-addr', '127.0.0.1:{}'.format(rpc_port)])
    cmd.extend(['-tag', 'rpc={}'.format(rpc_port)])
    cmd.extend(['-tag', 'timestamp={}'.format(time.time())])

    service = config.service or ip
    cmd.extend(['-tag', 'service={}'.format(service)])

    service_port = config.service_port
    cmd.extend(['-tag', 'service_port={}'.format(service_port)])

    cmd.extend(['-tag', 'ports={}'.format(
        encode_ports(get_ports()['ports']))])

    async_hook()
    async_save_info()

    subprocess.check_call(cmd)


if __name__ == '__main__':
    main()
