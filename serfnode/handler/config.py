import os
import uuid

from mischief.actors.pipe import get_local_ip
import yaml


def read_serfnode_yml():
    with open('/serfnode.yml') as input:
        conf = yaml.load(input) or {}
        return conf.get('serfnode') or {}


yml = read_serfnode_yml()


role = os.environ.get('ROLE') or yml.get('role') or 'no_role'
peer = os.environ.get('PEER') or yml.get('peer')
ip = (os.environ.get('SERF_IP') or yml.get('serf_ip') or
      get_local_ip('8.8.8.8'))
bind_port = os.environ.get('SERF_PORT') or yml.get('serf_port') or 7946
node = os.environ.get('NODE_NAME') or uuid.uuid4().hex
rpc_port = os.environ.get('RPC_PORT') or 7373
service = os.environ.get('SERVICE_IP') or yml.get('service_ip')
service_port = os.environ.get('SERVICE_PORT') or yml.get('service_port') or 0

app_ports = yaml.load(os.environ.get('APP_PORTS', '')) or []
app_volumes = yaml.load(os.environ.get('APP_VOLUMES', '')) or []
app_volumes_from = yaml.load(os.environ.get('APP_VOLUMES_FROM', '')) or []
