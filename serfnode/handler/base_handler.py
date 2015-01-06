import yaml
import os
import socket
import fcntl
import struct

from serf_master import SerfHandler
from utils import with_payload, truncated_stdout, with_member_info
from info import NODE_INFO, NODE_PORTS
import supervisor
import docker_utils
import utils
import serf


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
        app_volumes = os.environ.get('APP_VOLUMES')
        if app_volumes:
            self.volumes = ' '.join(
                '-v {}'.format(vol)
                for vol in yaml.load(app_volumes))
        else:
            self.volumes = ''
        self.setup()

    def setup(self):
        self.update()
        self.docker_run()

    def docker_run(self):
        if docker_utils.DOCKER_RUN:
            supervisor.start('docker_run.conf', target='docker_run')

    @truncated_stdout
    @with_payload
    def where(self, role=None):
        my_role = os.environ.get('ROLE') or 'no_role'
        if my_role == role:
            print(NODE_INFO)

    @truncated_stdout
    @with_payload
    def ports(self, role=None):
        my_role = os.environ.get('ROLE') or 'no_role'
        if my_role == role:
            print(NODE_PORTS)


    def update(self):
        etc = utils.read_etc_hosts()
        new = serf.serf_all_hosts()
        recent = serf.serf_recent_hosts(new)
        etc.update(recent)
        utils.write_etc_hosts(etc)

    @with_member_info
    def member_join(self, members):
        self.update()

    @with_member_info
    def member_failed(self, members):
        self.update()

    @with_member_info
    def member_leave(self, members):
        self.update()
