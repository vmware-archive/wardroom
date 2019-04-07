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
import jinja2
import os
import re
import subprocess
import tempfile
import yaml


def vagrant_status():
    """ Run `vagrant status` and parse the current vm state """
    node_state = {}

    output = subprocess.check_output(['vagrant', 'status'])
    for i, line in enumerate(output.splitlines()):
        if i < 2:
            continue
        parts = re.split(r'\s+', line)
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


def run_ansible(playbook, inventory_file, extra_args=[]):
    """ Run ansible playbook via subprocess.
    We do not want to link ansible as it is GPL """

    ssh_tempfile = tempfile.mkstemp()
    vagrant_ssh_config(ssh_tempfile[1])

    ansible_env = os.environ.copy()
    ansible_env['ANSIBLE_CONFIG'] = "ansible.cfg"
    ansible_env['ANSIBLE_SSH_ARGS'] = os.getenv('ANSIBLE_SSH_ARGS', '')
    ansible_env['ANSIBLE_SSH_ARGS'] += " -F %s" % (ssh_tempfile[1])
    subprocess.call([
        "ansible-playbook",
        "-i",
        inventory_file,
        playbook] + extra_args, env=ansible_env)


def get_vagrant_provider():
        return os.environ.get('VAGRANT_DEFAULT_PROVIDER', 'virtualbox')


def get_loadbalancer_ip():

    provider = get_vagrant_provider()
    if provider == 'virtualbox':
        return "10.10.10.3"

    output = subprocess.check_output(['vagrant', 'ssh-config', 'loadbalancer'])
    for line in output.split('\n'):
        match = re.match(r'\s*HostName\s+(.*)', line)
        if match:
            return match.groups()[0]
    raise Exception("Could not determine loadbalancer IP")


def merge_dict(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            merge_dict(value, node)
        else:
            destination[key] = value

    return destination


def generate_inventory(config, node_state={}):
    """ from node_state generate a dynamic ansible inventory.
        return temporary inventory file path """
    inventory = {
        "loadbalancer": {"hosts": {}},
        "etcd": {"hosts": {}},
        "primary_master": {"hosts": {}},
        "masters": {"hosts": {}},
        "nodes": {"hosts": {}},
    }
    for node, state in node_state.items():
        if state == "running":
            if node.startswith('master'):
                inventory["masters"]["hosts"][node] = {}
                inventory["etcd"]["hosts"][node] = {}
            elif node.startswith("node"):
                inventory["nodes"]["hosts"][node] = {}
            elif node.startswith("loadbalancer"):
                inventory["loadbalancer"]["hosts"][node] = {}

    inventory['primary_master']["hosts"]["master1"] = {}

    data = None
    with open(config, 'rb') as fh:
        render_args = {
            'loadbalancer_ip': get_loadbalancer_ip(),
            'vagrant_provider': get_vagrant_provider(),
        }
        config = jinja2.Template(fh.read()).render(**render_args)
        data = yaml.load(config)

    inventory = merge_dict(data, inventory)

    temp_file = tempfile.mkstemp()[1]
    with open(temp_file, 'w') as fh:
        yaml.dump(inventory, fh)

    print "Running with inventory:\n"
    print yaml.dump(inventory)
    print

    return temp_file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', default='install',
                        choices=['install'])
    parser.add_argument('config')
    args, extra_args = parser.parse_known_args()

    node_state = vagrant_status()

    start_vms = False
    for node, state in node_state.items():
        if state != 'running':
            start_vms = True
            break

    if start_vms:
        vagrant_up()

    node_state = vagrant_status()
    inventory_file = generate_inventory(args.config, node_state)

    playbook = "%s.yml" % args.action
    run_ansible(playbook, inventory_file, extra_args)


if __name__ == '__main__':
    main()
