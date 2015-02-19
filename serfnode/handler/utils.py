from __future__ import print_function

from functools import wraps
import json
import os
import sys
import traceback
import cStringIO
import re
import shutil
import socket

import mischief.actors.pipe as p
import mischief.actors.actor as a
import docker_utils
import config

MAX_OUTPUT = 1000


def truncated_stdout(f):
    """Decorator to truncate stdout to final `MAX_OUTPUT` characters. """

    @wraps(f)
    def wrapper(*args, **kwargs):
        old_stdout = sys.stdout
        old_stdout.flush()
        sys.stdout = cStringIO.StringIO()
        out = ''
        try:
            result = f(*args, **kwargs)
            stdout = sys.stdout.getvalue()
            out = stdout + '\nSUCCESS' if stdout else ''
            return result
        except Exception:
            out = traceback.format_exc() + '\nERROR'
        finally:
            sys.stdout = old_stdout
            print(out[-MAX_OUTPUT:], end='')
    return wrapper


def with_payload(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        payload = json.loads(sys.stdin.read())
        kwargs.update(payload)
        return f(*args, **kwargs)
    return wrapper


def with_member_info(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        kwargs['members'] = list(member_info(sys.stdin.readlines()))
        return f(*args, **kwargs)
    return wrapper


def member_info(lines):
    for line in lines:
        member = {}
        parts = line.split()
        member['node'] = parts[0]
        member['ip'] = parts[1]
        member['role'] = parts[2]
        member['tags'] = dict(part.split('=') for part in parts[3].split(','))
        yield member


def serf_aware_spawn(actor, name, **kwargs):
    """Spawn actor and save address info in ``/actor_info``. """

    ip = config.ip
    kwargs['ip'] = ip
    proc = a.spawn(actor, **kwargs)
    try:
        os.makedirs('/actors')
    except OSError:
        pass
    with open('/actors/{}'.format(name), 'w') as f:
        identifier, ip, port = proc.address()
        json.dump({'name': identifier, 'ip': ip, 'port': port}, f)
    return proc


def get_ports(cid=None):
    """Get the ports mapping for the container `cid`."""

    def _get_ports(cid):
        cinfo = docker_utils.client.inspect_container(cid)
        for port, host_ports in cinfo['NetworkSettings']['Ports'].items():
            if host_ports is not None:
                yield port, [host['HostPort'] for host in host_ports]

    cid = cid or socket.gethostname()
    return {
        'ports': dict(_get_ports(cid)),
        'ip': config.ip
    }


def encode_ports(ports):
    """Dict[str, Any] -> str"""

    protocols = {'tcp': 't', 'udp': 'u'}

    def one_port():
        for internal, externals in ports.items():
            internal_port, protocol = internal.split('/')
            all_externals = ','.join(externals)
            short_proto = protocols[protocol]
            yield ('{internal_port}{short_proto}{all_externals}'.
                   format(**locals()))

    return '|'.join(one_port())


def decode_ports(port_string):
    """str -> Dict[str, Any]"""

    def split_one_map(map_str):
        internal, externals = re.split('[tu]', map_str)
        internal_port = '{}/{}'.format(
            internal, 'tcp' if 't' in map_str else 'u')
        return internal_port, externals.split(',')

    return dict(map(split_one_map,
                    [port for port in port_string.split('|') if port]))
