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

WARDROOM_DATA_DIR = "wardroom_data"


def get_data_path(path):
    path = os.path.join(sys.prefix, WARDROOM_DATA_DIR, path)
    if not os.path.isdir(path):
        raise Exception("Could not find package directory for %s" % path)
    return path
