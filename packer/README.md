# Building Wardroom Images

This directory contains tooling for building base images for use as nodes in Kubernetes Clusters. [Packer](https://www.packer.io) is used for building these images.

- [Building Wardroom Images](#building-wardroom-images)
    - [Prerequisites](#prerequisites)
        - [Prerequisites for all images](#prerequisites-for-all-images)
        - [Prerequisites for Amazon Web Services](#prerequisites-for-amazon-web-services)
        - [Prerequisites for Google Cloud](#prerequisites-for-google-cloud)
    - [Building Images](#building-images)
        - [Build Variables](#build-variables)
        - [Limiting Images to Build](#limiting-images-to-build)
        - [Building the AWS AMIs](#building-the-aws-amis)
        - [Building Google Cloud Images](#building-google-cloud-images)
    - [Testing Images](#testing-images)
    - [Deploying Images](#deploying-images)
        - [AWS](#aws)
        - [Google Cloud](#google-cloud)
    - [Updating the Heptio AWS Quick Start Images](#updating-the-heptio-aws-quick-start-images)
    - [Appendix](#appendix)
        - [GCP Service Account Credentials](#gcp-service-account-credentials)

## Prerequisites

### Prerequisites for all images

- [Packer](https://www.packer.io/docs/installation.html)
- [Ansible](http://docs.ansible.com/ansible/latest/intro_installation.html) version >= 2.4.0.0

### Prerequisites for Amazon Web Services

- An AWS account
- The AWS CLI installed and configured

### Prerequisites for Google Cloud

- A Google Cloud account
- The gcloud CLI installed and configured
- A precreated service account json file

## Building Images

### Build Variables

The following variables can be overriden when building images using the `-var` option when calling `packer build`:

| Variable | Default | Description |
|----------|---------|-------------|
| build_version | unset | A unique build version for the image |
| kubernetes_version | 1.9.5-00 | Kubernetes Version to install |
| kubernetes_cni_version | 0.6.0-00 | CNI Version to install |

For exmaple, to build all images for use with Kubernetes 1.8.9 for build version 1:

```sh
packer build -var kubernetes_version=1.8.9-00 -var build_version=1
```

There are additional variables that may be set that affect the behavior of specific builds or packer post-processors. `packer inspect packer.json` will list all available variables and their default values.

### Limiting Images to Build

If packer build is run without specifying which images to build, then it will attempt to build all configured images. `packer inspect packer.json` will list the configured builders. The `--only` option can be specified when running `packer build` to limit the images built.

For example, to build only the AWS Ubuntu image:

```sh
packer build -var build_version=`git rev-parse HEAD` --only=ami-ubuntu packer.json
```

### Building the AWS AMIs

Building AWS images requires setting additional variables not set by default. The `aws-us-east-1.json` file is provided as an example.

To build both the Ubuntu and CentOS AWS AMIs:

```sh
packer build -var-file aws-us-east-1.json -var build_version=`git rev-parse HEAD` --only=ami-centos,ami-ubuntu packer.json
```

### Building Google Cloud Images

Building Google Cloud images requires setting the `GOOGLE_APPLICATION_CREDENTIALS` environment variable and setting some additional that are not set by default. The `gcp-source-images.json` file is provided as an example.

To build only the Ubuntu Google Cloud Image:

```sh
export GOOGLE_APPLICATION_CREDENTIALS=<YOUR CREDENTIAL FILE>
export GOOGLE_PROJECT_ID=<PROJECT_ID>
packer build -var-file=gcp-source-images.json -var build_version=`git rev-parse HEAD` -only gcp-ubuntu packer.json
```

## Testing Images

Connect remotely to an instance created from the image and run the Node Conformance tests using the following commands:

```sh
wget https://dl.k8s.io/$(< /etc/kubernetes_community_ami_version)/kubernetes-test.tar.gz
tar -zxvf kubernetes-test.tar.gz
cd kubernetes/platforms/linux/amd64
sudo ./ginkgo --nodes=8 --flakeAttempts=2 --focus="\[Conformance\]" --skip="\[Flaky\]|\[Serial\]" ./e2e_node.test -- --k8s-bin-dir=/usr/bin
```

## Deploying Images

### AWS

There is a helper script to aid in seeding built AMI's to all other AWS regions. This script can be installed from the root of this repository by running `python3 setup.py install`.

```sh
wardroom aws copy-ami -r <SOURCE_REGION> <SOURCE_AMI>
```

### Google Cloud

Unlike AWS, Google Cloud Images are not limited to specific regions, so no further steps are needed to use the create images.

## Updating the Heptio AWS Quick Start Images

- Build the base image

    ```sh
    packer build -var-file aws-us-east-1.json -var build_version=`git rev-parse HEAD` --only=ami-ubuntu packer.json
    ```
- Run Node Conformance against the built image
- Deploy the image using copy-ami
- Update the [Quick Start](https://github.com/heptio/aws-quickstart) to use the new images

## Appendix

### GCP Service Account Credentials

[Create a GCP service account](https://www.packer.io/docs/builders/googlecompute.html#running-without-a-compute-engine-service-account)

You'll need to download the credential file after creating your account. Make sure you don't commit it, it contains secrets.

You'll also need to make note of the "project ID" you wish to run the container in. It's a string, and you can find it at the top of the Google Cloud Console, or with `gcloud projects list`.