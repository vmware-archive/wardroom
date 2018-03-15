building images
===============
Building images for Kubernetes is easily accomplished with the [Packer](https://github.com/hashicorp/packer) and the templates found in this directory.

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [building images](#building-images)
- [Amazon](#amazon)
    - [aws-quickstart](#aws-quickstart)
    - [prerequisites](#prerequisites)
    - [build the AMI's](#build-the-amis)
    - [testing the AMIs](#testing-the-amis)
    - [deployment](#deployment)
- [Azure](#azure)
    - [prerequisites](#prerequisites-1)

<!-- markdown-toc end -->


Amazon
========

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
/path/to/packer build -var-file <YOUR REGION>.json -var kubernetes_version=<YOUR K8S VERSION> -var kubernetes_cni_version=<YOUR K8S CNI VERSION> -var build_version=`git rev-parse HEAD` -only ami-ubuntu-16.04 packer.json
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


Azure
=====

prerequisites
-------------
Building an Azure image is much more complicated than building an AMI. It is in
fact so complicated that Packer provides a shell script to set up all the
resources you need. [ Run the shell script ][script].


After running that script, save the JSON blob output somewhere safe (DO NOT
commit it anywhere! It contains secrets.) You can now use this file as a vars
file. Then, you can build packer with an invocation like this:

```
$ packer build -var-file=<path to your file> -var kubernetes_version=1.9.2-00 -var kubernetes_cni_version=0.6.0-00 -var build_version=`git rev-parse HEAD` -only azure-ubuntu  packer.json
```

[script]: https://www.packer.io/docs/builders/azure-setup.html#guided-setup

Creating the image ------------------ The script will spit out a bunch of URLs,
which can be very confusing. If you go into the azure console, however, you will
not see your image in [VM Images][images]. That is because this packer crosses a
virtual hard drive, not a full VM image. To boot a machine, you'll first need to
[create one][create].

Paste the `OSDiskUri` from the packer output into the "Storage Blob" field. Make
sure you set the image type to `Linux`. You can use the defaults for everything
else.

After you've created this image, you can use this to create new VMs.

[images]: https://portal.azure.com/#blade/HubsExtension/Resources/resourceType/Microsoft.Compute%2Fimages
[create]: https://portal.azure.com/#create/Microsoft.Image-ARM

