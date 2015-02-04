#!/usr/bin/env python
import os
import sys

import supervisor
import yaml
import docker_utils


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


def spawn_children():
    """Read /serfnode.yml and start containers"""

    print("Spawning children")
    if not os.path.exists('/serfnode.yml'):
        return

    with open('/serfnode.yml') as input:
        containers = yaml.load(input) or {}
        for name, run_stmt in containers.items():
            supervisor.install_launcher(name, all_volumes() + ' ' + run_stmt)


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
    serfnode.spawn(all_volumes())


def check_docker_access():
    """Check that we have access to the docker socket"""

    try:
        version = docker_utils.client.version()
        print('Access to docker successful: Docker {}, api {}'
              .format(version['Version'], version['ApiVersion']))
    except Exception:
        print('Serfnode needs access to the docker socket.')
        print('For easy access, if you are a trustful person, use:')
        print('')
        print('    docker run -v /:/host ...')
        print('')
        sys.exit(1)


def main():
    check_docker_access()
    spawn_children()
    spawn_docker_run()
    spawn_py()


if __name__ == '__main__':
    main()
