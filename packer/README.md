# Building Wardroom Images

This directory contains tooling for building base images for use as nodes in Kubernetes clusters. [Packer](https://www.packer.io/) is used for building the images

## Prerequisites

Prerequisites for all images:

- [Packer](https://www.packer.io/docs/installation.html)
- [Ansible](http://docs.ansible.com/ansible/latest/intro_installation.html) version >= 2.4.0.0

Prerequisites for building AMIs for use in Amazon Web Services:

- An AWS account
- The AWS CLI installed and configured

Prerequisites for building QEMU qcow2 images:

- qemu

## Building Images

### Build Variables

The following variables can be overriden when building images using the `-var` option when calling `packer build`:

| Variable | Default | Description |
|----------|---------|-------------|
| build_version | unset | A unique build version for the image |
| kubernetes_version | 1.9.3-00 | Kubernetes Version to install |
| kubernetes_cni_version | 0.6.0-00 | CNI Version to install |

For exmaple, to build all images for use with Kubernetes 1.8.9 for build version 1:

```bash
packer build -var kubernetes_version=1.8.9-00 -var build_version=1 --only=qemu-ubuntu-16.04 packer.json
```

### Limiting Images to Build

If packer build is run without specifying which images to build, then all configured images will be built. This currently includes QEMU images and AWS AMI images for Ubuntu 16.04 and CentOS 7. The `--only` option can be specified when running `packer build` to limit the images built.

To build only the QEMU Ubuntu image:

```bash
packer build -var build_version=`git rev-parse HEAD` --only=qemu-ubuntu-16.04 packer.json
```

To build only the QEMU CentOS image:

```bash
packer build -var build_version=`git rev-parse HEAD` --only=qemu-centos-7.4 packer.json
```

To build both the Ubuntu and CentOS AWS AMIs:

```bash
packer build -var build_version=`git rev-parse HEAD` --only=ami-centos-7.4,ami-ubuntu-16.04 packer.json
```

## Testing Images

Connect remotely to an instance created from the image and run the Node Conformance tests using the following commands:

```bash
wget https://dl.k8s.io/v1.9.3/kubernetes-test.tar.gz
tar -zxvf kubernetes-test.tar.gz
cd kubernetes/platforms/linux/amd64
sudo ./ginkgo --nodes=8 --flakeAttempts=2 --focus="\[Conformance\]" --skip="\[Flaky\]|\[Serial\]" ./e2e_node.test -- --k8s-bin-dir=/usr/bin
```

## Deploying Images

### AWS

There is a helper script to aid in seeding built AMI's to all other AWS regions. This script can be installed with `python3 setup.py install`.

```bash
copy-ami -r <SOURCE_REGION> -i <SOURCE_AMI> [-q]
```

## Updating the AWS Quick Start Images

- Build the base image

    ```bash
    packer build -var-file us-east-1.json -var build_version=`git rev-parse HEAD` --only=ami-ubuntu-16.04 packer.json
    ```
- Run Node Conformance against the built image
- Deploy the image using copy-ami
- Update the [Quick Start](https://github.com/heptio/aws-quickstart) to use the new images