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

# A simple tool for provisioning Vagrant hosts in parallel.

import argparse
import json
import os
import subprocess
import sys
import ConfigParser

from wardroom_provision.profile import Profile

WARDROOM_DEFAULT_PLAYBOOK = "swizzle.yml"


def run_ansible(inventory_file, ssh_config=None, ssh_user=None, extra_vars=[],
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
    return subprocess.call(cmd, env=ansible_env)


def _load_profiles():
    profile_path = os.getenv('WARDROOM_PROFILE_PATH', './profiles')
    profiles = {}

    for file in os.listdir(profile_path):
        if file.endswith(".yml") or file.endswith(".yaml"):
            fullpath = os.path.join(profile_path, file)
            profile = Profile.from_yaml(fullpath)
            if profile:
                profiles[profile.name] = profile

    return profiles


def _get_profile(name):
    profiles = _load_profiles()
    if name in profiles:
        return profiles[name]
    raise Exception("Profile %s not found" % name)


def provision(args, extra_args=[]):
    profile = _get_profile(args.profile)
    provisioner = profile.provisioner
    provisioner.provision()

    inventory_file = provisioner.generate_inventory()
    ssh_config = provisioner.ssh_config()

    for playbook in (args.pre_playbook, args.playbook,
                     args.post_playbook,):
        if not playbook:
            continue

        rc = run_ansible(inventory_file, ssh_config,
                ssh_user=profile.ssh_username,
                extra_vars=profile.extra_vars,
                extra_args=extra_args,
                playbook=playbook)
        if rc:
            sys.exit(rc)
        break


def teardown(args, extra_args=[]):
    profile = _get_profile(args.profile)
    provisioner = profile.provisioner
    provisioner.teardown()


def profile_list(args, extra_args=[]):
    profiles = _load_profiles()
    for _, profile in profiles.items():
        print "%s - %s" % (profile.name, profile.description)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    provision_parser = subparsers.add_parser('provision')
    provision_parser.add_argument('profile')
    provision_parser.add_argument('--pre-playbook')
    provision_parser.add_argument('--playbook',
                                  default=WARDROOM_DEFAULT_PLAYBOOK)
    provision_parser.add_argument('--post-playbook')
    provision_parser.set_defaults(func=provision)

    teardown_parser = subparsers.add_parser('teardown')
    teardown_parser.add_argument('profile')
    teardown_parser.set_defaults(func=teardown)

    profile_parser = subparsers.add_parser('profile')
    profile_subparsers = profile_parser.add_subparsers()

    profile_list_parser = profile_subparsers.add_parser('list')
    profile_list_parser.set_defaults(func=profile_list)

    args, extra_args = parser.parse_known_args()
    args.func(args, extra_args)


if __name__ == '__main__':
    main()
