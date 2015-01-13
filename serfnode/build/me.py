#!/usr/bin/python

import json
import os
import time


def main():
    while not os.path.exists('/agent_up'):
        time.sleep(0.1)
    node = json.load(open('/node_info'))
    print('{}:{}'.format(node['ip'], node['bind_port']))


if __name__ == '__main__':
    main()
