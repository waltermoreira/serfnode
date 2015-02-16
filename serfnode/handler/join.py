#!/usr/bin/env python
"""
Launch a serf node.

The role of the node is retrieved from the environment variable ``ROLE``.

The node will join a cluster, if the ``CONTACT`` variable specifies an
address.

"""

import subprocess
import time
import json
import multiprocessing

from utils import get_ports, encode_ports
import config
import pipe


def start_info_writer():
    def _handler(obj):
        try:
            old = json.load(open('/children'))
        except IOError:
            old = []
        old.append(obj)
        with open('/children', 'w') as f:
            f.write(json.dumps(old))

    t = multiprocessing.Process(target=pipe.server,
                                args=('/tmp/info_writer', _handler))
    t.start()


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

    service = config.service
    cmd.extend(['-tag', 'service={}'.format(service)])

    service_port = config.service_port
    cmd.extend(['-tag', 'service_port={}'.format(service_port)])

    cmd.extend(['-tag', 'ports={}'.format(
        encode_ports(get_ports()['ports']))])

    start_info_writer()
    subprocess.check_call(cmd)


if __name__ == '__main__':
    main()
