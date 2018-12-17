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
import socket
import time


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
    def teardown(self):
        return None

    @abc.abstractproperty
    def hosts(self):
        return None

    def wait_for_ssh(self, port=22, retries=10, interval=5):
        for i in range(0, retries):
            found_all = True
            for host in self.hosts:
                print "Checking host %s for ssh" % (host)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex((host, port))
                if result != 0:
                    found_all = False
                    break

            if not found_all:
                print "Waiting on ssh to become available"
                time.sleep(interval)
            else:
                break


