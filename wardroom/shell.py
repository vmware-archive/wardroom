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

import argparse
import logging
import sys

from wardroom.cluster import cluster_profile_list, cluster_provision, cluster_teardown  # noqa
from wardroom.cluster.provision import WARDROOM_DEFAULT_PLAYBOOK
from wardroom.image import get_aws_regions, get_builder_names, image_aws_distribute, image_build  # noqa


def _setup_logger(level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)
    log_handler = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter(fmt='%(asctime)s %(threadName)s %(name)s '
                            '%(levelname)s: %(message)s',
                            datefmt='%F %H:%M:%S')
    log_handler.setFormatter(fmt)
    logger.addHandler(log_handler)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # image
    image_parser = subparsers.add_parser('image')
    image_subparsers = image_parser.add_subparsers()

    # image build
    image_build_parser = image_subparsers.add_parser('build')
    image_build_parser.add_argument('build_version',
                                    help='unique build string for the image')
    image_build_parser.add_argument('--builders', '-b',
                                    choices=get_builder_names(),
                                    nargs='+', help="name of builders to use")
    image_build_parser.set_defaults(func=image_build)

    # image aws
    image_aws_parser = image_subparsers.add_parser('aws')
    image_aws_subparsers = image_aws_parser.add_subparsers()

    # image aws distribute
    image_aws_distrib_parser = image_aws_subparsers.add_parser('distribute')
    image_aws_distrib_parser.add_argument('region')
    image_aws_distrib_parser.add_argument('ami')
    image_aws_distrib_parser.add_argument('--limit', '-l',
                                          choices=get_aws_regions(),
                                          nargs='+',
                                          help="limit destination regions")
    image_aws_distrib_parser.set_defaults(func=image_aws_distribute)

    # cluster
    cluster_parser = subparsers.add_parser('cluster')
    cluster_subparsers = cluster_parser.add_subparsers()

    # cluster provision
    cluster_provision_parser = cluster_subparsers.add_parser('provision')
    cluster_provision_parser.add_argument('profile')
    cluster_provision_parser.add_argument('--pre-playbook')
    cluster_provision_parser.add_argument('--playbook',
                                          default=WARDROOM_DEFAULT_PLAYBOOK)
    cluster_provision_parser.add_argument('--post-playbook')
    cluster_provision_parser.set_defaults(func=cluster_provision)

    # cluster teardown
    cluster_teardown_parser = cluster_subparsers.add_parser('teardown')
    cluster_teardown_parser.add_argument('profile')
    cluster_teardown_parser.set_defaults(func=cluster_teardown)

    # cluster profile
    cluster_profile_parser = cluster_subparsers.add_parser('profile')
    cluster_profile_subparsers = cluster_profile_parser.add_subparsers()

    # cluster profile list
    cluster_profile_list_parser = cluster_profile_subparsers.add_parser('list')
    cluster_profile_list_parser.set_defaults(func=cluster_profile_list)

    args, extra_args = parser.parse_known_args()

    log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG
    _setup_logger(log_level)

    args.func(args, extra_args)


if __name__ == '__main__':
    main()
