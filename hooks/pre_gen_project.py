#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-
# File: pre_gen_project.py

import datetime
import json

now = datetime.datetime.now()
options = json.loads(open('../cookiecutter.json').read())
options['year'] = now.strftime('%Y')
options['release_date'] = now.strftime('%d-%m-%Y')

with open('../cookiecutter.json', 'w') as file:
    file.write(json.dumps(options, indent=2))
