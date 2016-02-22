#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
load_config
~~~~~~~~~~~

Load the config file given the path to its containing directory.
"""

import json
import sys
import os

if len(sys.argv) > 1:
    filepath = sys.argv[1]
else:
    filepath = './matchbot/'

configfile = os.path.join(filepath, 'config.json')
with open(configfile, 'rb') as configf:
    config = json.loads(configf.read())


def load_config(filepath):
    configfile = os.path.join(filepath, 'config.json')
    with open(configfile, 'rb') as configf:
        config = json.loads(configf.read())
    return config
