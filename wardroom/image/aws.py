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

import logging
import time
import yaml

import boto3

LOG = logging.getLogger(__name__)


def _copy_to_region(image, source_region, dest_region):
    session = boto3.session.Session(region_name=dest_region)
    local_client = session.client('ec2')
    LOG.info("Copying image to region %s" % dest_region)
    resp = local_client.copy_image(
        Name=image.name,
        SourceImageId=image.image_id,
        SourceRegion=source_region,
    )
    local_ec2 = session.resource('ec2')
    new_image = local_ec2.Image(resp['ImageId'])
    return (new_image, dest_region)


def _make_public_and_tag(image, region, desc):
    # wait up to 20 minutes...hopefully less
    for i in range(0, 240):
        LOG.debug("Waiting for image to become available...")
        image.load()
        if image.state == 'available':
            image.modify_attribute(
                LaunchPermission={
                    'Add': [{'Group': 'all'}]
                }
            )
            # Can only modify one attribute at a time
            image.modify_attribute(Description={'Value': desc})
            LOG.info("region %d ami %d is now available" % (region, image.id))
            break
        time.sleep(5)


def get_aws_regions():
    session = boto3.session.Session()
    client = session.client('ec2')

    regions = []
    for region in client.describe_regions()['Regions']:
        regions.append(region['RegionName'])
    return regions


def image_aws_distribute(args, extra_args={}):
    source_region = args.region
    source_ami = args.ami
    limit = args.limit

    session = boto3.session.Session(region_name=source_region)
    dest_regions = get_aws_regions()
    dest_regions.remove(source_region)
    dest_regions.sort()

    LOG.debug("detected %d regions" % len(dest_regions))
    image = session.resource('ec2').Image(source_ami)
    if not image:
        raise Exception("could not find ami: %s", source_ami)

    description = ""
    for tag in image.tags:
        description += "%s=%s " % (tag['Key'], tag['Value'])

    LOG.debug("Copying images to regions")
    new_images = [(image, source_region)]
    for region in dest_regions:
        if limit and region not in limit:
            LOG.debug("Skipping region %s due to --limit" % region)
            continue

        new_image = _copy_to_region(image, source_region, region)
        new_images.append(new_image)

    metadata = {}
    for new_image, region in new_images.items():
        metadata[region] = {"64": new_image}
        _make_public_and_tag(new_image, region, description)

    LOG.info("Images successfully copied. Image metadata:\n%s" %
             yaml.dumps(metadata))
