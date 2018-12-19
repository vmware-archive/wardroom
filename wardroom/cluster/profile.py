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

from collections import OrderedDict
from tabulate import tabulate

from wardroom import get_data_path
from wardroom.cluster.provisioners.profile import Profile

DEFAULT_PACKAGE_PROFILES = get_data_path('profiles')


def _load_profiles():
    profile_path = os.getenv('WARDROOM_PROFILE_PATH', DEFAULT_PACKAGE_PROFILES)
    profiles = {}

    for file in os.listdir(profile_path):
        if file.endswith(".yml") or file.endswith(".yaml"):
            fullpath = os.path.join(profile_path, file)
            profile = Profile.from_yaml(fullpath)
            if profile:
                profiles[profile.name] = profile

    return profiles


def get_profile(name):
    profiles = _load_profiles()
    if name in profiles:
        return profiles[name]
    raise Exception("Profile %s not found" % name)


def cluster_profile_list(args, extra_args=[]):
    profiles = _load_profiles()

    headers = ["name", "description"]
    rows = []

    profs = OrderedDict(sorted(profiles.items(), key=lambda t: t[0]))
    for _, profile in profs.items():
        rows.append([profile.name, profile.description])
    print (tabulate(rows, headers=headers, tablefmt="psql"))
