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

    return (new_image, region)


def make_public_and_tag(image, region, desc):
    while True:
        image.load()
        if image.state == 'available':
            image.modify_attribute(
                LaunchPermission={
                    'Add': [{'Group': 'all'}]
                }
            )
            # Can only modify one attribute at a time
            image.modify_attribute(Description={'Value': desc})
            logger.info("region {} ami {} is available".format(region, image.id))
            break
        time.sleep(5)


def encode_desc(dict_):
    return " ".join("{0}={1}".format(*item) for item in dict_.items())


def copy_ami(args):
    if args.quiet:
        logger.setLevel(logging.WARN)

    default_region = boto3.session.Session(region_name=args.region)

    client = default_region.client('ec2')
    regions = [region['RegionName']
               for region in client.describe_regions()['Regions']
               if region['RegionName'] != args.region
              ]
    regions.sort()

    logger.info("detected {} regions".format(len(regions)))

    image = default_region.resource('ec2').Image(args.ami_id)
    description = encode_desc({i['Key']: i['Value'] for i in image.tags or []})

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
        make_public_and_tag(image, region, description)

