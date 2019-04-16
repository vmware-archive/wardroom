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
| kubernetes_version | 1.13.2-00 | Kubernetes Version to install |
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

#### Required Permissions to Build the AWS AMIs

The [Packer documentation for the Amazon AMI builder](https://www.packer.io/docs/builders/amazon.html) supplies a suggested set of minimum permissions. However, Wardroom has been successfully tested with the following IAM permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:Describe*",
                "ec2:TerminateInstances",
                "ec2:StartInstances",
                "ec2:CreateSnapshot",
                "ec2:CreateImage",
                "ec2:RunInstances",
                "ec2:StopInstances",
                "ec2:CreateKeyPair",
                "ec2:DeleteKeyPair",
                "ec2:CreateSecurityGroup",
                "ec2:DeleteSecurityGroup",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:CreateTags",
                "ec2:DeleteVolume"
            ],
            "Resource": "*"
        }
    ]
}
```

### Building Google Cloud Images

Building Google Cloud images requires setting the `GOOGLE_APPLICATION_CREDENTIALS` environment variable and providing the IDs of the source images. For the latter, the `gcp-source-images.json` file is provided as an example.

To build only the Ubuntu Google Cloud Image:

```sh
export GOOGLE_APPLICATION_CREDENTIALS=<YOUR CREDENTIAL FILE>
packer build -var-file=gcp-source-images.json -var build_version=`git rev-parse HEAD` -var project_id=<your-project-id-here> -only gcp-ubuntu packer.json
```

#### Permissions Required to Build Google Cloud Images

The account used by Wardroom (as specified by the `GOOGLE_APPLICATION_CREDENTIALS` environment variable) must have the following permissions in order for Wardroom to function as expected:

```
compute.disks.create
compute.disks.delete
compute.disks.useReadOnly
compute.images.create
compute.images.delete
compute.images.get
compute.instances.create
compute.instances.delete
compute.instances.get
compute.instances.setMetadata
compute.instances.setServiceAccount
compute.instances.start
compute.instances.stop
compute.machineTypes.get
compute.subnetworks.use
compute.subnetworks.useExternalIp
compute.zones.get
```

### Building Oracle Cloud Infrastructure (OCI) Images

Building Oracle Cloud Infrastructure (OCI) images requires a correct configuration for the Oracle CLI as outlined in the "CLI Configuration Information" section of [this page](https://docs.cloud.oracle.com/iaas/Content/API/Concepts/sdkconfig.htm), althoug the Oracle CLI does not need to be installed (Packer will use the values in the configuration file).

You will also need the following pieces of information:

* The Oracle Cloud ID (OCID) of the compartment where the build VM will be instantiated (you can use the root compartment, whose OCID is equal to the tenancy OCID)
* The name of the availability domain where the build VM will be instantiated
* The OCID for the subnet that corresponds to the availability domain where the build VM will be instantiated

To build an OCI image:

```sh
packer build -var-file oci-us-phoenix-1.json -var build_version=`git rev-parse HEAD` -var oci_availability_domain="<name of availability domain>" -var oci_compartment_ocid="<OCID of compartment>" -var oci_subnet_ocid="<OCID of subnet in specified availability domain>" -only=oci-ubuntu packer.json
```

## Testing Images

After our images are created, we want to prove that the images can be used to build conformant clusters. The conformance testing suite tests clusters, not single nodes -- so we have to spin up a single node cluster
and run the tests inside that cluster.

Connect remotely to an instance created from the image and run the Node Conformance tests using the following commands:

```sh
sudo kubeadm init --pod-network-cidr=192.168.0.0/16
sudo chown $(id -u):$(id -g) /etc/kubernetes/admin.conf
export KUBECONFIG=/etc/kubernetes/admin.conf


kubectl create -f https://docs.projectcalico.org/v3.3/getting-started/kubernetes/installation/hosted/kubernetes-datastore/calico-networking/1.7/calico.yaml
kubectl create -f https://docs.projectcalico.org/v3.3/getting-started/kubernetes/installation/hosted/rbac-kdd.yaml


# Remove all the taints from the node -- simply adding tolerations to the conformance deployment didn't work
kubectl patch nodes $(hostname) -p '{"spec":{"taints":[]}}'

# Get the yaml to run the conformance tests, and replace the source image repo to use the 
# globally accessible image repo, instead of the Kubernetes internal one.
# This yaml was created along with the 1.14 release, but can be used with 1.13, and 
# it will up updated with future releases. (Again, this only works >=1.13)
wget https://raw.githubusercontent.com/kubernetes/kubernetes/master/cluster/images/conformance/conformance-e2e.yaml
sed -i 's/k8s.gcr.io/gcr.io\/google-containers/' conformance-e2e.yaml

# Will also need to go in and update the version number of the image to add the trailing "patch version" part
# The pulled yaml will only have major.minor.
# So, for example, with v1.14, you'll need to update the image to 1.14.0
# The valid conformance test images can be found here:
# gcr.io/google-containers/conformance-amd64

# Add to "value" for E2E_SKIP env var
\\[Flaky\\]|\\[Serial\\]|\\[sig-network\\]|Container Lifecycle Hook

# Finally, run the tests -- and leave it alone for about an hour.
kubectl create -f conformance-e2e.yaml
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

If you want to use a service account for use with Wardroom, you'll also need to grant the service account the ServiceAccountUser role in order for Wardroom to function properly.

You'll also need to make note of the "project ID" you wish to run the container in. It's a string, and you can find it at the top of the Google Cloud Console, or with `gcloud projects list`.
