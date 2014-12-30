#!/usr/bin/env python
"""
Launch a serf node.

The role of the node is retrieved from the environment variable ``ROLE``.

The node will join a cluster, if the ``CONTACT`` variable specifies an
address.

"""

import bisect
import os
import subprocess
import uuid
import time

from utils import save_info
from mischief.actors.pipe import get_local_ip


def find_port(start=1234):
    """Find an unused port starting at ``start``. """

    out = subprocess.check_output('netstat -antup'.split())
    used_ports = sorted(set(int(line.split()[3].split(':')[-1])
                            for line in out.splitlines()[2:]))
    return _find(used_ports, start)


def _find(lst, x):
    if not lst:
        return x
    idx = bisect.bisect_left(lst, x)
    if len(lst) <= idx:
        return x
    if lst[idx] == x:
        return _find(lst[idx:], x+1)
    else:
        return x


def main():
    role = os.environ.get('ROLE') or 'no_role'
    cmd = ('serf agent -event-handler=/handler/handler.py '
           '-log-level=debug -tag role={role}'
           .format(**locals()).split())

    contact = os.environ.get('PEER')
    if contact:
        cmd.extend(['-join', contact])

    ip = os.environ.get('IP') or get_local_ip('8.8.8.8')
    bind_port = os.environ.get('SERF_PORT') or find_port(start=7946)

    cmd.extend(['-advertise', '{}:{}'.format(ip, bind_port)])
    cmd.extend(['-tag', 'ip={}'.format(ip),
                '-tag', 'serf_port={}'.format(bind_port)])
    cmd.extend(['-bind', '0.0.0.0:{}'.format(bind_port)])

    node = os.environ.get('NODE_NAME') or uuid.uuid4().hex
    cmd.extend(['-node', node])

    rpc_port = os.environ.get('RPC_PORT') or find_port(start=7373)
    cmd.extend(['-rpc-addr', '127.0.0.1:{}'.format(rpc_port)])
    cmd.extend(['-tag', 'rpc={}'.format(rpc_port)])
    cmd.extend(['-tag', 'timestamp={}'.format(time.time())])

    service = os.environ.get('SERVICE_IP') or ip
    cmd.extend(['-tag', 'service={}'.format(service)])

    service_port = os.environ.get('SERVICE_PORT') or 0
    cmd.extend(['-tag', 'service_port={}'.format(service_port)])

    save_info(node, ip, bind_port, rpc_port)

    subprocess.check_call(cmd)


if __name__ == '__main__':
    main()
