#!/usr/bin/env python
import os

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


def spawn_children():
    """Read /serfnode.yml and start containers"""

    print("Spawning children")
    if not os.path.exists('/serfnode.yml'):
        return

    with open('/serfnode.yml') as input:
        containers = yaml.load(input) or {}
        for name, run_stmt in containers.items():
            supervisor.install_launcher(name, run_stmt)


def spawn_docker_run():
    if docker_utils.DOCKER_RUN:
        supervisor.install_docker_run(docker_utils.DOCKER_RUN)


def main():
    spawn_children()
    spawn_docker_run()


if __name__ == '__main__':
    main()
