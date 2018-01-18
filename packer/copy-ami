#!/usr/bin/env python3

import argparse
import logging
import sys
import time

import boto3

logger = logging.getLogger(name=__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
logger.addHandler(handler)

yaml_template ='''
    {}:
      '64': {}
'''.strip('\r\n')

parser = argparse.ArgumentParser(description='Copy an image to all available regions')
parser.add_argument('-r', '--region', default='us-east-1')
parser.add_argument('-i', '--ami-id', required=True)
parser.add_argument('-q', '--quiet', action='store_true')

def copy_to_region(image, region):
    session = boto3.session.Session(region_name=region)
    local_client = session.client('ec2')
    logger.info("creating image in region {}".format(region))
    resp = local_client.copy_image(
        Name=image.name,
        SourceImageId=image.image_id,
        SourceRegion=args.region,
        )
    local_ec2 = session.resource('ec2')
    new_image = local_ec2.Image(resp['ImageId'])
    new_image.create_tags(Tags=image.tags)
    
    return (new_image, region)

def wait_for_ready(image, region):
    while True:
        image.load()
        if image.state == 'available':
            image.modify_attribute(
                LaunchPermission={
                    'Add': [{'Group': 'all'}]
                }
            )
            logger.info("region {} ami {} is available".format(region, image.id))
            break
        time.sleep(5)

if __name__ == "__main__":
    args = parser.parse_args()

    if args.quiet:
        logger.setLevel(logging.WARN)

    default_region = boto3.session.Session(region_name=args.region)

    client = default_region.client('ec2')
    regions = [region['RegionName']
               for region in client.describe_regions()['Regions']
               if region['RegionName'] != args.region
              ]

    logger.info("detected {} regions".format(len(regions)))

    image = default_region.resource('ec2').Image(args.ami_id)

    # copy to all regions
    images = [copy_to_region(image, region) for region in regions]
    # Add the original
    images.append((image, args.region))


    # print out the YAML
    for (image, region) in images:
        print(yaml_template.format(region, image.id))

    logger.info("waiting for all images to be available. In the mean time,"
                "that YAML can be pasted into the quickstart template.")
    # wait for all images to be available
    for (image, region) in images:
        wait_for_ready(image, region)

