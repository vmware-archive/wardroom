# Copyright (c) 2017 Craig Tracey <ctracey@heptio.com>
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

# A simple tool for provisioning Vagrant hosts in parallel.
### WARNING: there is no error checking and this is not well tested! ###

import argparse
import os
import re
import subprocess
import tempfile
import sys
import ConfigParser


def vagrant_status():
    """ Run `vagrant status` and parse the current vm state """
    node_state = {}

    output = subprocess.check_output(['vagrant', 'status'])
    for i, line in enumerate(output.splitlines()):
        if i < 2:
            continue
        parts = re.split('\s+', line)
        if len(parts) == 3:
            node_state[parts[0]] = parts[1]
        elif len(parts) == 4:
            node_state[parts[0]] = " ".join(parts[1:3])
    return node_state


def vagrant_up():
    """ Bring up the vm's with a `vagrant up`"""
    subprocess.call(['vagrant', 'up', '--parallel'])


def vagrant_ssh_config(tempfile):
    """ Get the current ssh config via `vagrant ssh-config` """
    output = subprocess.check_output(['vagrant', 'ssh-config'])
    with open(tempfile, 'w') as fh:
        fh.write(output)


def run_ansible(inventory_file, extra_args=[]):
    """ Run ansible playbook via subprocess.
    We do not want to link ansible as it is GPL """

    ssh_tempfile = tempfile.mkstemp()
    vagrant_ssh_config(ssh_tempfile[1])

    ansible_env = os.environ.copy()
    ansible_env['ANSIBLE_CONFIG'] = ".ansible.cfg"
    ansible_env['ANSIBLE_SSH_ARGS'] = os.getenv('ANSIBLE_SSH_ARGS', '')
    ansible_env['ANSIBLE_SSH_ARGS'] += " -F %s" % (ssh_tempfile[1])
    subprocess.call([
        "ansible-playbook",
        "--extra-vars",
        '{"vagrant_host": true}',
        "-i",
        inventory_file,
        "swizzle.yml"] + extra_args, env=ansible_env)


def generate_inventory(node_state={}):
    """ from node_state generate a dynamic ansible inventory.
        return temporary inventory file path """
    inventory = {
        "masters": [],
        "nodes": []
    }
    for node, state in node_state.items():
        if state == "running":
            if node.startswith('master'):
                inventory["masters"].append(node)
            elif node.startswith("node"):
                inventory["nodes"].append(node)

    parser = ConfigParser.ConfigParser(allow_no_value=True)
    for key, vals in inventory.items():
        parser.add_section(key)
        for val in vals:
            parser.set(key, val)

    temp_file = tempfile.mkstemp()[1]
    with open(temp_file, 'w') as fh:
        parser.write(fh)

    return temp_file


def main():
    parser = argparse.ArgumentParser()
    args, extra_args = parser.parse_known_args()

    node_state = vagrant_status()
    inventory_file = generate_inventory(node_state)

    start_vms = False
    for node, state in node_state.items():
        if state != 'running':
            start_vms = True
            break

    if start_vms:
        vagrant_up()

    run_ansible(inventory_file, extra_args)


if __name__ == '__main__':
    main()
