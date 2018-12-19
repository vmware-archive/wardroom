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

import os
import sys

from wardroom.cluster.profile import get_profile
from wardroom.util import run_command

WARDROOM_DEFAULT_PLAYBOOK = "swizzle.yml"


def _run_ansible(inventory_file, ssh_config=None, ssh_user=None, extra_vars=[],
                 extra_args=[], playbook=WARDROOM_DEFAULT_PLAYBOOK):
    """ Run ansible playbook via subprocess.
    We do not want to link ansible as it is GPL """

    ansible_env = os.environ.copy()
    ansible_env['ANSIBLE_CONFIG'] = ".ansible.cfg"
    ansible_env['ANSIBLE_HOST_KEY_CHECKING'] = "false"

    if ssh_config:
        ansible_env['ANSIBLE_SSH_ARGS'] = os.getenv('ANSIBLE_SSH_ARGS', '')
        ansible_env['ANSIBLE_SSH_ARGS'] += " -F %s" % (ssh_config)

    cmd = [
        "ansible-playbook",
        "-i",
        inventory_file,
    ]

    if ssh_user:
        cmd += ["-u", ssh_user]

    if extra_args:
        cmd += extra_args

    if extra_vars:
        cmd += ['--extra-vars', extra_vars]

    cmd.append(playbook)
    print "Wardroom running %s" % (cmd)
    return run_command(cmd, 'swizzle', env=ansible_env)


def cluster_provision(args, extra_args=[]):
    profile = get_profile(args.profile)
    provisioner = profile.provisioner
    provisioner.provision()

    inventory_file = provisioner.generate_inventory()
    ssh_config = provisioner.ssh_config()

    for playbook in (args.pre_playbook, args.playbook,
                     args.post_playbook,):
        if not playbook:
            continue

        rc = _run_ansible(inventory_file, ssh_config,
                          ssh_user=profile.ssh_username,
                          extra_vars=profile.extra_vars,
                          extra_args=extra_args,
                          playbook=playbook)
        if rc:
            sys.exit(rc)
        break
