# Building Images

Building images for Kubernetes is easily accomplished with the [Packer](https://github.com/hashicorp/packer) and the templates found in this directory.

## General Prerequisites

- [Packer](https://www.packer.io/docs/installation.html)
- [Ansible](http://docs.ansible.com/ansible/latest/intro_installation.html) version >= 2.4.0.0

## AWS Quickstart

This directory contains the build scripts for the AWS AMI that's used by Heptio's [AWS Quick Start](https://github.com/heptioaws-quickstart). Heptio's AMI is, in turn, built on Ubuntu 16.04 LTS.

### Prerequisites

To build the AMI, you need:

- An AWS account
- The AWS CLI installed and configured

### Build the AMI's

From this directory, simply run:

```
/path/to/packer build -var-file <YOUR REGION>.json -var kubernetes_version=<YOUR K8S VERSION> -var kubernetes_cni_version=<YOUR K8S CNI VERSION> -var build_version=`git rev-parse HEAD` packer.json
```
This will build AMI images in the us-east AWS region (additional region support to follow).

You may limit which images build by adding the `-only=` flag to Packer.

### Testing the AMIs

```
wget https://dl.k8s.io/v1.9.3/kubernetes-test.tar.gz
tar -zxvf kubernetes-test.tar.gz
cd kubernetes/platforms/linux/amd64
sudo ./ginkgo --nodes=8 --flakeAttempts=2 --focus="\[Conformance\]" --skip="\[Flaky\]|\[Serial\]" ./e2e_node.test -- --k8s-bin-dir=/usr/bin
```

### Deployment
----------
There is a helper script to aid in seeding built AMI's to all other AWS regions.
You can install them with `python3 setup.py install`.

```
copy-ami -r <SOURCE_REGION> -i <SOURCE_AMI> [-q]
```

## OpenStack Quickstart

To get started with pushing Kubernetes-ready images to OpenStack, you'll need to make sure you meet the following requirements:

- Have a running OpenStack environment
- Have OpenStack credentials that can push images

Please note that it is a good idea to brush up on the variables that can be set by reading through the [Packer documentation for OpenStack found here](https://www.packer.io/docs/builders/openstack.html). Once you have done so, please perform the following to build an image and push it to OpenStack:

First, copy the `openstack.json` file found in this folder; rename it to something like `my-custom-options.json`. Next, to build an image and push it OpenStack, run the following command:

```
/path/to/packer build -var-file <COPIED-FILENAME>.json -var kubernetes_version=<YOUR K8S VERSION> -var kubernetes_cni_version=<YOUR K8S CNI VERSION> -var build_version=`git rev-parse HEAD` packer.json
```

If everything was successful, you'll have pushed an image to OpenStack which can be readily used to deploy VMs at your dispense. These images can be treated like any other images in OpenStack and even deployed via [Terraform](https://www.terraform.io/). Please note that Packer cannot build images without a correct OpenStack configuration; which greatly varies based on your unique OpenStack installations. This configuration has been tested with a local dev environment and AWS.
