import json
import socket
import fcntl
import struct
import glob

from serf_master import SerfHandler
from utils import with_payload, truncated_stdout, with_member_info
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


def update_etc():
    etc = read_etc()
    new = serf.serf_all_hosts()
    recent = serf.serf_recent_hosts(new)
    etc.update(recent)
    write_etc(etc)


def read_etc():
    with open('/etc/hosts') as f:
        lines = f.readlines()
        etc = [line.strip().split()
               for line in lines
               if not line.startswith('#')]
    return {host: line[0] for line in etc for host in line[1:]}


def write_etc(etc):
    ip_hosts = {}
    for host, ip in etc.items():
        ip_hosts.setdefault(ip, []).append(host)
        content = ''.join(
            ' '.join([ip] + hosts)+'\n' for ip, hosts in ip_hosts.items())
        with open('/etc/hosts', 'w') as f:
            f.write(content)


def notify():
    with open('/agent_up', 'w') as f:
        f.write('')


def update():
    update_nodes_info()
    update_etc()


class BaseHandler(SerfHandler):

    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        self.setup()
        notify()

    @classmethod
    def init(cls):
        pass

    def setup(self):
        pass

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

    @with_member_info
    def member_join(self, members):
        update()

    @with_member_info
    def member_failed(self, members):
        update()

    @with_member_info
    def member_leave(self, members):
        update()
