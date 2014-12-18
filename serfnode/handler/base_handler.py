import json
import os
import socket
import fcntl
import struct

from serf_master import SerfHandler
from utils import with_payload, truncated_stdout


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


class BaseHandler(SerfHandler):

    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        self.setup()

    def setup(self):
        pass

    @truncated_stdout
    @with_payload
    def where(self, role=None):
        my_role = os.environ.get('ROLE', 'no_role')
        if my_role == role:
            print(my_info())

    @truncated_stdout
    @with_payload
    def where_actor(self, role=None):
        my_role = os.environ.get('ROLE', 'no_role')
        if my_role == role:
            print(actor_info())


def my_info():
    ip = os.environ.get('ADVERTISE') or get_ip_address('eth0')
    return json.dumps({'ip': ip,
                       'bind': os.environ['SERF_TAG_BIND'],
                       'advertise': os.environ.get('SERF_TAG_ADV'),
                       'rpc': os.environ['SERF_TAG_RPC']})


def actor_info():
    try:
        actor_files = os.listdir('/actors')
    except OSError:
        return json.dumps({})
    info = {}
    for actor_file in actor_files:
        info[actor_file] = json.load(open('/actors/{}'.format(actor_file)))
    return json.dumps(info)

