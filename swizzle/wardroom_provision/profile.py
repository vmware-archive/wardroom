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

import yaml

from jinja2 import Template
from stevedore.driver import DriverManager

PROVISIONER_NAMESPACE = "wardroom_provision.provisioners"


class Profile(object):

    def __init__(self, name, description, provisioner_name,
                 provisioner_args={}, ssh_username=None,
                 ansible_overrides={}):
        self.name = name
        self.description = description
        self.provisioner_name = provisioner_name
        self.provisioner_args = provisioner_args
        self.ssh_username = ssh_username
        self.ansible_overrides = ansible_overrides
        self._provisioner = None

    def _get_provisioner(self):
        mgr = DriverManager(namespace=PROVISIONER_NAMESPACE,
                            name=self.provisioner_name,
                            invoke_kwds=self.provisioner_args,
                            invoke_on_load=True)
        return mgr.driver

    @property
    def provisioner(self):
        if not self._provisioner:
            self._provisioner = self._get_provisioner()
        return self._provisioner

    @property
    def extra_vars(self):
        variables = []
        for key, val in self.ansible_overrides.items():
            t = Template(val)
            newval = t.render(**self.provisioner.exported_vars)
            variables.append("%s=%s" % (key , newval))
        return " ".join(variables)

    @staticmethod
    def from_yaml(filename):
        with open(filename, 'rb') as fh:
            data = yaml.load(fh)
            return Profile(**data)

