# Copyright 2018, Craig Tracey <craigtracey@gmail.com>
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations

import re
import yaml

from jsonpath_ng.ext import parse
from requests import get

from ansible.module_utils.basic import AnsibleModule


def _check_condition(manifest, condition):
    expr = parse(condition['expression'])
    matches = expr.find(manifest)

    found = True
    for match in matches:
        if not re.match(condition['value'], match.value):
            found = False
            break

    return found


def _execute_modification(manifest, modification):
    expr = parse(modification['expression'])
    matches = expr.find(manifest)

    updated = False
    for match in matches:
        out = match.full_path.update(manifest, modification['value'])
        if out != manifest:
            updated = True
    return updated


def main():

    fields_spec = dict(
        expression=dict(required=True, type='str'),
        value=dict(required=True, type='str'),
    )

    rules_spec = dict(
        conditions=dict(default=[], type='list', elements='dict',
                        options=fields_spec),
        modifications=dict(default=[], type='list', elements='dict',
                           options=fields_spec),
    )

    module = AnsibleModule(
        argument_spec=dict(
            manifest_url=dict(required=True, type='str'),
            rules=dict(type='list', default=[], elements='dict',
                       options=rules_spec),
            output_path=dict(required=True, type='str'),
        )
    )

    changed = False
    try:
        resp = get(module.params['manifest_url'])
        resp.raise_for_status()

        # we may get multi-doc yaml
        manifests = list(yaml.load_all(resp.text))
        for manifest in manifests:
            for rule in module.params['rules']:

                conditions_met = True
                for condition in rule['conditions']:
                    if not _check_condition(manifest, condition):
                        conditions_met = False
                        break

                if not conditions_met:
                    break

                for modification in rule['modifications']:
                    status = _execute_modification(manifest, modification)
                    if status:
                        changed = status

        with open(module.params['output_path'], 'wb') as fh:
            fh.write(yaml.dump_all(manifests, explicit_start=True))

    except Exception as e:
        module.exit_json(msg=e)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
