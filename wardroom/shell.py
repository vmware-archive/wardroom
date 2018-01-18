import argparse

from wardroom.aws import copy_ami


def main():

    parser = argparse.ArgumentParser(description='A wardroom helper utility')
    subparsers = parser.add_subparsers()

    aws_parser = subparsers.add_parser('aws')
    aws_subparsers = aws_parser.add_subparsers()

    aws_copy_ami_parser = aws_subparsers.add_parser('copy-ami')
    aws_copy_ami_parser.add_argument('-r', '--region', default='us-east-1')
    aws_copy_ami_parser.add_argument('-i', '--ami-id', required=True)
    aws_copy_ami_parser.add_argument('-q', '--quiet', action='store_true')
    aws_copy_ami_parser.set_defaults(func=copy_ami)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
