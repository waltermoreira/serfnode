#!/usr/bin/env python
import os

import supervisor
import yaml
import docker_utils


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
