#!/usr/bin/env python

import argparse
import subprocess
import sys


def render_host(ip, user, key=None):
    with open('/deploy/hosts', 'w') as hosts:
        key_line = ('ansible_ssk_private_key_file={}'.format(key)
                    if key is not None else '')
        hosts.write(
            '[all]\n'
            '{} ansible_ssh_user={} {}\n'.format(ip, user, key_line))


def ansible(args):
    ask = '--ask-pass' if not args.key else ''
    cmd = ('ansible-playbook {} -i /deploy/hosts /deploy/deploy.yml'
           .format(ask))
    subprocess.check_call(cmd.split())


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