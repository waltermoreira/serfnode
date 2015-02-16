#!/usr/bin/python

import json
import os
import time


def main():
    while not os.path.exists('/agent_up'):
        time.sleep(0.1)
    node_id = json.load(open('/me.json'))['id']
    node = json.load(open('/serfnodes_by_id.json'))[node_id]
    print('{}:{}'.format(node['serf_ip'], node['serf_port']))


if __name__ == '__main__':
    main()
