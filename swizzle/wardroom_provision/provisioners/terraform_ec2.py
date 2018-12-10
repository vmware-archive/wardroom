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
import subprocess
import sys
import tempfile
import ConfigParser

from wardroom_provision.provisioners import Provisioner

from jsonpath_ng.ext import parse

JSONPATH_EXPRESSIONS = {
    'masters': '$..modules[?(@.path[1]==masters)].outputs.cluster_instance_public_addresses.value',
    'nodes': '$..modules[?(@.path[1]==workers)].outputs.cluster_instance_public_addresses.value',
    'primary_master': '$..modules[?(@.path[1]==masters)].outputs.cluster_instance_public_addresses.value[0]',
    'etcd': '$..modules[?(@.path[1]==masters)].outputs.cluster_instance_public_addresses.value',
}

JSONPATH_EXPORTED_VARS = {
    'master_elb_dns_name': "$..modules[*].resources['aws_elb.master_elb'].primary.attributes.dns_name",
}

DEFAULT_TFSTATE_PATH = './terraform.tfstate'


class TerraformEC2Provisioner(Provisioner):

    def __init__(self, terraform_path=None, tfstate_path=DEFAULT_TFSTATE_PATH):
        super(TerraformEC2Provisioner, self).__init__()
        self.terraform_path = terraform_path
        self.tfstate_path = tfstate_path
        self._exported_vars = None

    def provision(self):
        cmd = ['terraform', 'init']
        if self.terraform_path:
            cmd += [self.terraform_path]
        print cmd
        subprocess.call(cmd)

        cmd = ['terraform', 'apply']
        if self.terraform_path:
            cmd += [self.terraform_path]
        subprocess.call(cmd)

    def ssh_config(self):
        return None

    def ansible_extra_args(self):
        return {
            'kubernetes_primary_interface': 'eth0'
        }

    def generate_inventory(self):
        filename = self.tfstate_path
        config = ConfigParser.RawConfigParser(allow_no_value=True)

        state = None
        with open(filename, 'rb') as fh:
            state = json.load(fh)

        for group, expression in JSONPATH_EXPRESSIONS.items():
            config.add_section(group)

            expr = parse(expression)
            for match in expr.find(state):
                value = match.value
                if not isinstance(value, list):
                    value = [value]
                for ip in value:
                    config.set(group, ip)

        config.write(sys.stdout)
        temp_file = tempfile.mkstemp()[1]
        with open(temp_file, 'w') as fh:
            config.write(fh)
        return temp_file

    @property
    def exported_vars(self):
        if not self._exported_vars:
            variables = {}

            filename = self.tfstate_path
            state = None
            with open(filename, 'rb') as fh:
                state = json.load(fh)

            for varname, expression in JSONPATH_EXPORTED_VARS.items():
                expr = parse(expression)
                for match in expr.find(state):
                    variables[varname] = match.value
            self._exported_vars = variables
        return self._exported_vars

    def teardown(self):
        raise NotImplemented()
