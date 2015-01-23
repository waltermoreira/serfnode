import json
import subprocess
import sys

import info
import utils


def serf(*args):
    args = list(args)
    rpc_port = info.NODE_INFO['rpc_port']
    args[1:1] = ['-rpc-addr', '127.0.0.1:{}'.format(rpc_port)]
    cmd = ['serf'] + args + ['-format=json']
    return json.loads(subprocess.check_output(cmd))


serf_json = serf


def serf_plain(*args):
    """Call serf with regular output"""

    args = list(args)
    rpc_port = info.NODE_INFO['rpc_port']
    args[1:1] = ['-rpc-addr', '127.0.0.1:{}'.format(rpc_port)]
    cmd = ['serf'] + args
    return subprocess.check_output(cmd)


def serf_event(name, *args):
    rpc_port = info.NODE_INFO['rpc_port']
    cmd = ['serf', 'event',
           '-rpc-addr', '127.0.0.1:{}'.format(rpc_port),
           name] + list(args)
    subprocess.check_call(cmd, stdout=sys.stderr)


def _query(name, service):
    rpc_port = info.NODE_INFO['rpc_port']
    cmd = ['serf', 'query',
           '-rpc-addr', '127.0.0.1:{}'.format(rpc_port),
           '-format=json', name,
           json.dumps({'role': service})]
    out = json.loads(subprocess.check_output(cmd))
    for node, response in out['Responses'].items():
        if response.endswith('SUCCESS'):
            yield json.loads(response[:-len('SUCCESS')])


def where(service):
    return _query('where', service)


def where_actor(service):
    return _query('where_actor', service)


def is_self(node):
    return serf('info')['agent']['name'] == node


def serf_all_hosts():
    members = serf('members')['members']
    hosts = {}
    for member in members:
        if member['status'] == 'alive':
            ip = member['tags']['service']
            role = member['tags']['role']
            timestamp = member['tags']['timestamp']
            port_mapping = utils.decode_ports(member['tags']['ports'])
            hosts.setdefault(role, []).append(
                {'ip': ip,
                 'timestamp': timestamp,
                 'ports': port_mapping})
    return hosts


def serf_recent_hosts(all_hosts):
    hosts = {}
    for role, info in all_hosts.items():
        ip = max(info, key=lambda it: it['timestamp'])['ip']
        hosts[role] = ip
    return hosts
