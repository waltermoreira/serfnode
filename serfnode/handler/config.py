import os
import uuid

from mischief.actors.pipe import get_local_ip


role = os.environ.get('ROLE') or 'no_role'
peer = os.environ.get('PEER')
ip = os.environ.get('IP') or get_local_ip('8.8.8.8')
bind_port = os.environ.get('SERF_PORT') or 7946
node = os.environ.get('NODE_NAME') or uuid.uuid4().hex
rpc_port = os.environ.get('RPC_PORT') or 7373
service = os.environ.get('SERVICE_IP') or ip
service_port = os.environ.get('SERVICE_PORT') or 0
