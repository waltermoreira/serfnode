#!/bin/bash

set -e
/handler/install.py
/usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf
