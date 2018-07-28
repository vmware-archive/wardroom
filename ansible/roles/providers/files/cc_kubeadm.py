# Copyright (C) 2018 Craig Tracey <craigtracey@gmail.com>
#
# This file is part of cloud-init. See LICENSE file for license information.

# Initialize a kubeadm cluster:
# kubeadm_init:
#   config: /home/user/kubeadm.config
#
# Add an additional controlplane instance:
# kubeadm_controlplane_join:
#   config: /home/user/kubeadm.config
#
# Add a worker instance:
# kubeadm_join:
#   config: /home/user/kubeadm.config

import os
import re

from cloudinit import util
from cloudinit.config.schema import validate_cloudconfig_schema
from cloudinit.distros import ALL_DISTROS
from cloudinit.settings import PER_INSTANCE

frequency = PER_INSTANCE
distros = [ALL_DISTROS]

SCHEMA = {
    'id': 'cc_kubeadm',
    'name': 'kubeadm',
    'title': 'bootstrap a kubernetes node',
    'distros': distros,
    'frequency': PER_INSTANCE,
    'type': 'object',
    'properties': {
        'type': 'object',
        'kubeadm_init': {
            'type': 'object',
            'required': ['config'],
            'properties': {
                'config': {'type': 'string'},
            },
            'additionalProperties': False,
        },
        'kubeadm_controlplane_join': {
            'type': 'object',
            'required': ['config'],
            'properties': {
                'config': {'type': 'string'},
            },
            'additionalProperties': False,
        },
        'kubeadm_join': {
            'type': 'object',
            'required': ['config'],
            'properties': {
                'config': {'type': 'string'},
            },
            'additionalProperties': False,
        },
        'additionalProperties': False,
    },
    'additionalProperties': False,
}


def run_kubeadm_init(config):
    cmd = ["/usr/bin/kubeadm", "init", "--config", config]
    util.subp(cmd, capture=False)



def run_kubeadm_join(config):
    cmd = ["/usr/bin/kubeadm", "join", "--config", config]
    util.subp(cmd, capture=False)


def handle(name, cfg, cloud, log, _args):
    """Handler method activated by cloud-init."""

    schema = SCHEMA
    validate_cloudconfig_schema(cfg, schema, strict=True)

    if 'kubeadm' not in cfg:
        log.debug("Skipping 'kubeadm' module as there is no config")
        return

    try:
        if 'kubeadm_init' in cfg['kubeadm']:
            run_kubeadm_init(cfg['kubeadm']['kubeadm_init']['config'])
        elif 'kubeadm_controlplane_join' in cfg['kubeadm']:
            run_kubeadm_join(cfg['kubeadm']['kubeadm_controlplane_join']['config'])
            # TODO: perform additional control plane join steps
        elif 'kubeadm_join' in cfg['kubeadm']:
            run_kubeadm_join(cfg['kubeadm']['kubeadm_join']['config'])
        else:
            log.debug("Skipping 'kubeadm' module as there is no subconfig")
            return
    except Exception as e:
        log.error("Failed to run kubeadm: %s" % e)
