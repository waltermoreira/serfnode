#!/usr/bin/env python

from __future__ import print_function

import argparse
import Queue
import subprocess
import sys
import threading

import yaml


def render_host(ip, user, key=None):
    with open('/deploy/hosts', 'w') as hosts:
        key_line = ('ansible_ssk_private_key_file={}'.format(key)
                    if key is not None else '')
        hosts.write(
            '[all]\n'
            '{} ansible_ssh_user={} {}\n'.format(ip, user, key_line))


def progress():
    queue = Queue.Queue()
    def _progress(queue):
        print('\n')
        while True:
            try:
                queue.get(timeout=1)
                print('\n')
                return
            except Queue.Empty:
                print('.', sep='', end='')
                sys.stdout.flush()
    t = threading.Thread(target=_progress, args=(queue,))
    t.daemon = True
    t.start()
    return queue


def ansible(args):
    ask = '--ask-pass' if not args.key else ''
    if args.deploy:
        playbook = 'deploy'
    elif args.stop:
        playbook = 'stop'
    elif args.docker:
        playbook = 'docker'
    else:
        print('need one of --deploy, --stop, --docker')
        return
    cmd = ('ansible-playbook {} -i /deploy/hosts /deploy/{}.yml'
           .format(ask, playbook))
    if playbook == 'stop':
        serfnode_name = subprocess.check_output(
            'cat /deploy/deploy.yml | grep serfnode_name | '
            'cut -f 2 -d: | head -1',
            shell=True).strip()
        cmd += ' -e serfnode_name={}'.format(serfnode_name)
    #p = progress()
    ansible_process = subprocess.Popen(cmd.split(),
                                       stderr=subprocess.PIPE,
                                       stdout=subprocess.PIPE)
    err = ansible_process.wait()
    #p.put(None)
    if err:
        print('Ansible playbook failed:')
        print(ansible_process.stderr.read())
        print(ansible_process.stdout.read())
        return
    if playbook == 'deploy':
        print(open('/tmp/me').read())


def main():
    args = parse_args(sys.argv[1:])
    render_host(args.ip, args.user, args.key)
    ansible(args)


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--deploy', action='store_true',
                        help='self-deploy to a host')
    parser.add_argument('--stop', action='store_true',
                        help='stop itself in a host')
    parser.add_argument('--docker', action='store_true',
                        help='install docker in remote host')
    parser.add_argument('--ip', nargs='?', metavar='IP',
                        type=str, default='172.17.42.1',
                        help='ip of host to deploy')
    parser.add_argument('--peer', nargs='?', metavar='IP:PORT',
                        type=str,
                        help='location of a peer in the cluster')
    parser.add_argument('--user', nargs='?', metavar='USER',
                        type=str, default='root',
                        help='remote username to ssh')
    parser.add_argument('--key', nargs='?', metavar='FILE',
                        type=str,
                        help=('location of the ssh private key for '
                              'accessing the host'))
    return parser.parse_args(args)


if __name__ == '__main__':
    main()