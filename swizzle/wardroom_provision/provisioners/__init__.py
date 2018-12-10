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

import abc


class Provisioner(object):

    @abc.abstractmethod
    def provision(self):
        return None

    @abc.abstractmethod
    def generate_inventory(self):
        return None

    @abc.abstractmethod
    def ssh_config(self):
        return None

    @abc.abstractmethod
    def exported_vars(self):
        return None

    @abc.abstractmethod
    def teaardown(self):
        return None
