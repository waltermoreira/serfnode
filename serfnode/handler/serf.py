import json
import subprocess
import sys
import os
from itertools import tee, groupby

from file_utils import atomic_write
import utils
import config


def serf(*args):
    """Call serf with output in json format"""

    args = list(args)
    rpc_port = config.rpc_port
    args[1:1] = ['-rpc-addr', '127.0.0.1:{}'.format(rpc_port)]
    cmd = ['serf'] + args + ['-format=json']
    return json.loads(subprocess.check_output(cmd))


serf_json = serf


def serf_plain(*args):
    """Call serf with regular output"""

    args = list(args)
    rpc_port = config.rpc_port
    args[1:1] = ['-rpc-addr', '127.0.0.1:{}'.format(rpc_port)]
    cmd = ['serf'] + args
    return subprocess.check_output(cmd)


def serf_event(name, *args):
    """Send and event trough serf"""

    rpc_port = config.rpc_port
    cmd = ['serf', 'event',
           '-rpc-addr', '127.0.0.1:{}'.format(rpc_port),
           name] + list(args)
    subprocess.check_call(cmd, stdout=sys.stderr)


def serf_query(name, args):
    """
    :param name: str
    :param args: dict
    :return:
    """
    rpc_port = config.rpc_port
    cmd = ['serf', 'query',
           '-rpc-addr', '127.0.0.1:{}'.format(rpc_port),
           '-format=json', name,
           json.dumps(args)]
    out = json.loads(subprocess.check_output(cmd))
    for node, response in out['Responses'].items():
        if response.endswith('SUCCESS'):
            yield json.loads(response[:-len('SUCCESS')])


def _query(name, service):
    rpc_port = config.rpc_port
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
    """Return a dictionary of all hosts and their info"""

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


def all_nodes():
    """Return a dictionary of all nodes by role"""

    members = serf('members')['members']
    for member in members:
        if member['status'] == 'alive':
            role = member['tags']['role']
            serf_ip = member['addr'].split(':')[0]
            yield {'id': member['name'],
                   'role': role,
                   'serf_ip': serf_ip,
                   'serf_port': member['tags']['serf_port'],
                   'service_ip': member['tags'].get('service', serf_ip),
                   'service_port': member['tags']['service_port'],
                   'timestamp': member['tags']['timestamp'],
                   'ports': utils.decode_ports(member['tags']['ports'])}


def all_nodes_by_role_and_id():
    by_id, by_roles = tee(all_nodes())
    all_by_id = {o['id']: o for o in by_id}
    all_by_role = {r: list(x) for r, x in groupby(
        sorted(by_roles, key=lambda o: o['role']),
        key=lambda o: o['role'])}
    for loc in ['/', '/serfnode']:
        with atomic_write(os.path.join(loc, 'serfnodes_by_id.json')) as f:
            json.dump(all_by_id, f)
        with atomic_write(os.path.join(loc, 'serfnodes_by_role.json')) as f:
            json.dump(all_by_role, f)


def serf_recent_hosts(all_hosts):
    hosts = {}
    for role, info in all_hosts.items():
        ip = max(info, key=lambda it: it['timestamp'])['ip']
        hosts[role] = ip
    return hosts

