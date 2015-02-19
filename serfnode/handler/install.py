#!/usr/bin/env python
import os

import supervisor
import yaml
import docker_utils
import config


def collect_app_volumes():
    """Construct -v parameter to mount volumes in app."""

    app_volumes = os.environ.get('APP_VOLUMES')
    return (' '.join('-v {}'.format(vol)
                     for vol in yaml.load(app_volumes))
            if app_volumes else '')


def collect_app_volumes_from():
    """Construct --volumes_from parameter to mount volumes in app."""

    app_volumes_from = os.environ.get('APP_VOLUMES_FROM')
    return (' '.join('--volumes-from {}'.format(vol)
                     for vol in yaml.load(app_volumes_from))
            if app_volumes_from else '')


def all_volumes():
    return collect_app_volumes() + collect_app_volumes_from()


def wrap(op, values):
    return ' '.join('{}{}'.format(op, v) for v in values)


def install(pos, conf, master):
    name = conf.keys()[0]
    params = conf[name]

    links = wrap('--link=', params.get('links', []))
    ports = wrap('-p ', (params.get('ports', []) +
                         master.get('ports', []) +
                         config.app_ports))
    expose = wrap('--expose=', params.get('expose', []))
    volumes = wrap('-v ',
                   params.get('volumes', []) +
                   master.get('volumes', []) +
                   config.app_volumes)
    volumes_from = wrap(
        '--volumes-from=',
        params.get('volumes_from', []) +
        master.get('volumes_from', []) +
        config.app_volumes_from)
    all_env = params.get('environment', {})
    all_env.update(master.get('environment', {}))
    env = wrap(' -e ', ['"{}={}"'.format(k, v) for k, v in all_env.items()])
    working_dir = wrap('-w ', filter(None, [params.get('working_dir')]))
    entrypoint = wrap('--entrypoint=',
                      filter(None, [params.get('entrypoint')]))
    user = wrap('-u ', filter(None, [params.get('user')]))
    privileged = '--privileged' if params.get('privileged') else ''
    image = params['image']
    cmd = params.get('command', '')

    docker_run = ('{links} {ports} {expose} {volumes} '
                  '{volumes_from} {env} {working_dir} {entrypoint} '
                  '{user} {privileged} {image} {cmd}'
                  .format(**locals()))
    print("Child: docker run {}".format(' '.join(docker_run.split())))
    supervisor.install_launcher(name, docker_run, pos=pos)


def spawn_children():
    """Read /serfnode.yml and start containers"""

    if not os.path.exists('/serfnode.yml'):
        return

    print("Using serfnode.yml")
    with open('/serfnode.yml') as input:
        yml = yaml.load(input) or {}
        children = yml.get('children') or {}
        master = yml.get('serfnode') or {}
        for pos, child in enumerate(children):
            install(pos, child, master)


def spawn_docker_run():
    """Spawn a child from a DOCKER_RUN env variable"""

    if docker_utils.DOCKER_RUN:
        print("Using DOCKER_RUN")
        supervisor.install_docker_run(docker_utils.DOCKER_RUN,
                                      docker_utils.DOCKER_NAME)


def spawn_py():
    """Spawn children from a python file"""

    try:
        import serfnode
    except ImportError:
        return
    print("Using serfnode.py")
    serfnode.spawn(all_volumes())


def check_docker_access():
    """Check that we have access to the docker socket"""

    try:
        version = docker_utils.client.version()
        print('Access to docker successful: Docker {}, api {}'
              .format(version['Version'], version['ApiVersion']))
    except Exception:
        print('WARNING: Serfnode usually needs access to the docker socket.')
        print('For easy access, if you are a trustful person, use:')
        print('')
        print('    docker run -v /:/host ...')
        print('')


def main():
    check_docker_access()
    spawn_children()
    spawn_docker_run()
    spawn_py()


if __name__ == '__main__':
    main()
