import json
import os
import socket
import fcntl
import struct
import time

from serf_master import SerfHandler
from utils import with_payload, truncated_stdout, with_member_info
from info import NODE_INFO
import mischief.actors.actor as actor
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
    def where_actor(self, role=None):
        my_role = os.environ.get('ROLE') or 'no_role'
        if my_role == role:
            print(actor_info())

    def get_writer_ref(self):
        actor_info = json.load(open('/actors/EtcWriter'))
        return actor.ActorRef(
            (actor_info['name'], actor_info['ip'], actor_info['port']))

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
        

def actor_info():
    try:
        actor_files = os.listdir('/actors')
    except OSError:
        return json.dumps({})
    info = {}
    for actor_file in actor_files:
        info[actor_file] = json.load(open('/actors/{}'.format(actor_file)))
    return json.dumps(info)
