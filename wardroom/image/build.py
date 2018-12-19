# Copyright (c) 2018 Craig Tracey <ctracey@heptio.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os

from wardroom import get_data_path
from wardroom.util import run_command

DEFAULT_PACKER_TEMPLATE = "packer.json"
AWS_VAR_FILE = os.path.join(get_data_path('packer'), 'aws-us-east-1.json')


def get_builder_names():
    packer_dir = get_data_path('packer')
    packer_template = os.path.join(packer_dir, DEFAULT_PACKER_TEMPLATE)
    packer_data = None
    with open(packer_template, 'rb') as fh:
        packer_data = json.load(fh)

    builders = []
    for builder in packer_data['builders']:
        builders.append(builder['name'])
    return builders


def image_build(args, extra_args=None):
    cmd = [
        'packer',
        'build',
        '-var',
        'build_version=%s' % args.build_version,
        '-var-file',
        AWS_VAR_FILE,
    ]

    if args.builders:
        cmd += ['-only', ",".join(args.builders)]

    cmd += [DEFAULT_PACKER_TEMPLATE]
    run_command(cmd, 'packer')
