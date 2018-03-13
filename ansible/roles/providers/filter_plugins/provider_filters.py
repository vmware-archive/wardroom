# Provider Filters

from ansible import errors


def provider_from_builder_type(builder_type):
    ''' Returns normalized provider name '''
    if builder_type.startswith('amazon'):
        return 'aws'
    elif builder_type == 'qemu':
        return 'vagrant'
    else:
        raise errors.AnsibleFilterError('Unknown builder_type: {}'.format(builder_type))


# ---- Ansible filters ----
class FilterModule(object):
    ''' Provider Filters '''

    def filters(self):
        return {
            'provider_from_builder_type': provider_from_builder_type
        }