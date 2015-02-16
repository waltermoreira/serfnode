#!/usr/bin/env python

import json

import serf
import pipe


def handler(obj):
    name, payload = obj
    serf.serf_plain('event', name, json.dumps(payload))


if __name__ == '__main__':
    pipe.server('/serfnode/parent', handler)
