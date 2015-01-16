import os
import socket
import subprocess

import docker_utils
import docker
import jinja2
env = jinja2.Environment(loader=jinja2.FileSystemLoader('/programs'))


def supervisor_install(block, **kwargs):
    """Update supervisor with `block` config.

    - `block` is the name to a .conf template file (in directory
      `/programs`)
    - `kwargs` are the key/values to use in the template

    """
    conf_filename = '{}.conf'.format(kwargs['target'])
    template = env.get_template(block)
    kwargs.update({
        'DOCKER': docker_utils.DOCKER,
        'DOCKER_SOCKET': docker_utils.DOCKER_SOCKET,
        'DOCKER_RUN': docker_utils.DOCKER_RUN})
    conf = template.render(kwargs)
    with open(os.path.join(
            '/etc/supervisor/conf.d', conf_filename), 'w') as f:
        f.write(conf)


def supervisor_exec(*args):
    return subprocess.check_output(
        ['supervisorctl'] + list(args))


def supervisor_update():
    supervisor_exec('reread')
    supervisor_exec('update')


def start(block, **kwargs):
    supervisor_install(block, **kwargs)
    supervisor_update()
    supervisor_exec('start', '{}:*'.format(kwargs['target']))


def start_docker(target, cmdline, share_network=True):
    name = 'app_{}'.format(socket.gethostname())
    args = ['--name={}'.format(name)]
    if share_network:
        args.extend([
            '--net',
            'container:{}'.format(socket.gethostname())])
    args.append(cmdline)
    start('launcher.conf', target=target,
          ARGS=' '.join(args),
          NAME=name)


def stop(block):
    supervisor_exec('stop', '{}:*'.format(block))
