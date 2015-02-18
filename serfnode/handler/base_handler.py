import json
import os
import socket
import fcntl
import struct
import glob

from serf_master import SerfHandler
from utils import with_payload, truncated_stdout, with_member_info
import docker_utils
import serf
import config

NODE_INFO = ''
NODE_PORTS = ''


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


def update_nodes_info():
    serf.all_nodes_by_role_and_id()


def get_info(cid):
    sid = serf.serf_json('info')['agent']['name']
    inspect = docker_utils.client.inspect_container(cid)
    return {'id': sid, 'inspect': inspect}


def save_me(loc):
    with open(loc, 'w') as f:
        json.dump(get_info(socket.gethostname()), f)


def update_children():
    for child in glob.glob('/child_app_*'):
        cid = open(child).read()
        update_child(cid)


def update_child(cid):
    etc = read_etc(cid)
    new = serf.serf_all_hosts()
    recent = serf.serf_recent_hosts(new)
    etc.update(recent)
    write_etc(cid, etc)


def read_etc(cid):
    lines = docker_utils.docker('exec', cid, 'cat', '/etc/hosts').splitlines()
    etc = [line.strip().split()
           for line in lines
           if not line.startswith('#')]
    return {host: line[0] for line in etc for host in line[1:]}


def write_etc(cid, etc):
    ip_hosts = {}
    for host, ip in etc.items():
        ip_hosts.setdefault(ip, []).append(host)
        content = ''.join(
            ' '.join([ip] + hosts)+'\n' for ip, hosts in ip_hosts.items())
        docker_utils.docker(
            'exec', cid, 'bash', '-c',
            "echo '{}' > /etc/hosts".format(content))


class BaseHandler(SerfHandler):

    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        save_me('/me.json')
        save_me('/serfnode/parent.json')
        self.setup()
        self.notify()

    def setup(self):
        self.update()

    def notify(self):
        with open('/agent_up', 'w') as f:
            f.write('')

    @truncated_stdout
    @with_payload
    def where(self, role=None):
        my_role = config.role
        if my_role == role:
            print(NODE_INFO)

    @truncated_stdout
    @with_payload
    def ports(self, role=None):
        my_role = config.role
        if my_role == role:
            print(json.dumps(NODE_PORTS))

    def update(self):
        update_nodes_info()
        update_children()

    @with_member_info
    def member_join(self, members):
        self.update()

    @with_member_info
    def member_failed(self, members):
        self.update()

    @with_member_info
    def member_leave(self, members):
        self.update()
