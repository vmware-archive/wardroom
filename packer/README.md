building images
===============
Building images for Kubernetes is easily accomplished with the [Packer](https://github.com/hashicorp/packer) and the templates found in this directory.

aws-quickstart
--------------
This directory contains the build scripts for the AWS AMI that's used by Heptio's [AWS Quick Start](https://github.com/heptioaws-quickstart). Heptio's AMI is, in turn, built on Ubuntu 16.04 LTS.

prerequisites
-------------
To build the AMI, you need:

- [Packer](https://www.packer.io/docs/installation.html)
- [Ansible](http://docs.ansible.com/ansible/latest/intro_installation.html) version >= 2.4.0.0
- An AWS account
- The AWS CLI installed and configured

build the AMI's
---------------
From this directory, simply run:

```
$ /path/to/packer build -var-file <YOUR REGION>.json -var kubernetes_version=<YOUR K8S VERSION> -var kubernetes_cni_version=<YOUR K8S CNI VERSION> -var build_version=`git rev-parse HEAD` packer.json
```
This will build AMI images in the us-east AWS region (additional region support to follow).

You may limit which images build by adding the `-only=` flag to Packer.

build raw images
----------------
From this directory, run:
```
$ cloud-localds cloud.img cloud.cfg
$ /path/to/packer -var kubernetes_version=<YOUR K8S VERSION> -var kubernetes_cni_version=<YOUR K8S CNI VERSION> -var build_version=`git rev-parse HEAD` packer.json
```

deployment
----------
There is a helper script to aid in seeding built AMI's to all other AWS regions.
You can install them with `python3 setup.py install`.

```
copy-ami -r <SOURCE_REGION> -i <SOURCE_AMI> [-q]
```
