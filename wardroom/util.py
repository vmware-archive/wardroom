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
import subprocess

from wardroom import get_data_path


def run_command(command, data_path, env=None, fail_on_error=True):
    cwd = get_data_path(data_path)

    cmdenv = os.environ.copy()
    if env:
        cmdenv.update(env)

    print command
    print cwd
    rc = subprocess.call(command, cwd=cwd, env=cmdenv)

    if rc != 0:
        raise Exception("Command %s failed with exit %s" % (command, rc))
    return rc
