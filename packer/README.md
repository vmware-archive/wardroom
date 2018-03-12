<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [building images](#building-images)
- [Amazon](#amazon)
    - [aws-quickstart](#aws-quickstart)
    - [prerequisites](#prerequisites)
    - [build the AMI's](#build-the-amis)
    - [testing the AMIs](#testing-the-amis)
    - [deployment](#deployment)
- [Google Cloud](#google-cloud)
    - [build GCP images](#build-gcp-images)

<!-- markdown-toc end -->

building images
===============
Building images for Kubernetes is easily accomplished with the [Packer](https://github.com/hashicorp/packer) and the templates found in this directory.

Amazon
======

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
/path/to/packer build -var-file <YOUR REGION>.json -var kubernetes_version=<YOUR K8S VERSION> -var kubernetes_cni_version=<YOUR K8S CNI VERSION> -var build_version=`git rev-parse HEAD` packer.json
```
This will build AMI images in the us-east AWS region (additional region support to follow).

You may limit which images build by adding the `-only=` flag to Packer.

testing the AMIs
----------------
```
wget https://dl.k8s.io/v1.9.3/kubernetes-test.tar.gz
tar -zxvf kubernetes-test.tar.gz
cd kubernetes/platforms/linux/amd64
sudo ./ginkgo --nodes=8 --flakeAttempts=2 --focus="\[Conformance\]" --skip="\[Flaky\]|\[Serial\]" ./e2e_node.test -- --k8s-bin-dir=/usr/bin
```

deployment
----------
There is a helper script to aid in seeding built AMI's to all other AWS regions.
You can install them with `python3 setup.py install`.

```
copy-ami -r <SOURCE_REGION> -i <SOURCE_AMI> [-q]
```

Google Cloud
============

build GCP images
-----------------

[Create a GCP service account][packergcp].

You'll need to download the credential file after creating your account. Make
sure you don't commit it, it contains secrets.

You'll also need to make note of the "project ID" you wish to run the container
in. It's a string, and you can find it at the top of the Google Cloud Console,
or with `gcloud projects list`.

Then, call packer:

```
GOOGLE_APPLICATION_CREDENTIALS=<YOUR CREDENTIAL FILE> packer build -var kubernetes_version=<YOUR K8S VERSION> -var kubernetes_cni_version=<YOUR K8S CNI VERSION> -var build_version=`git rev-parse HEAD` -var project_id=<PROJECT_ID> -only gcp-ubuntu-16.04 packer.json
```

Google Cloud doesn't have public images in the same way that Amazon does, but
you can create VMs from any image in a project you have access to.

[packergcp]: https://www.packer.io/docs/builders/googlecompute.html#running-without-a-compute-engine-service-account
