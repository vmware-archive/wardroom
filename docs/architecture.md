# Wardroom Architecture

## Summary

Customers deploying Kubernetes need solutions to help simplify establishing a Kubernetes cluster. There are a number of different ways to go about this; two methods, in particular, involve creating Kubernetes-ready base images and orchestrating the process of bootstrapping a cluster. Wardroom provides functionality that addresses both of these use cases:

1. Wardroom provides a mechanism for users to create Kubernetes-ready base images that contain all the necessary prerequisites for running Kubernetes.

2. Wardroom provides orchestration around the process of bootstrapping a cluster.

## Motivation

As noted in the Summary above, customers and VMware personnel need a mechanism for streamlining the process of establishing a Kubernetes cluster from available infrastructure. Wardroom strives to provide such a mechanism.

### Goals

The following items **are** in scope for Wardroom:

* Wardroom must provide an "image generation" mechanism by which customers can create Kubernetes-ready base images. A _Kubernetes-ready image_ is defined as an OS image that has been prepared for Kubernetes and is ready to run `kubeadm` (or a tool automating `kubeadm`) to bootstrap a Kubernetes cluster.

* Wardroom must provide "cluster bootstrapping" functionality that orchestrates the process of bootstrapping a Kubernetes cluster, including bootstrapping a cluster from images that have not been previously prepared.

* Wardroom must support two Ubuntu LTS releases (the current and the previous LTS release) and the last major release of CentOS. Currently, this translates into supporting Ubuntu 16.04 (until the release of 20.04), Ubuntu 18.04, and CentOS 7.

* Wardroom must support the same versions of Kubernetes as the upstream community; that is, _N-2_, where _N_ represents the most recent release of Kubernetes. Currently, this means support for Kubernetes 1.14, 1.13, and 1.12.

### Non-Goals

The following items **are not** in scope for Wardroom:

* Wardroom does not attempt to automate the provisioning of infrastructure.

## Architecture

### Implementation Details

Currently, Wardroom is implemented as a set of [Ansible][1] roles and a set of [Packer][2] build files. Users use the Packer build files to invoke the Ansible roles in order to prepare images on a target platform. Other Ansible roles provide the orchestration functionality necessary to automate the bootstrapping of a cluster from scratch. Users must have the `ansible` and `packer` tools installed locally in order to use Wardroom's components.

### Extending Functionality

#### Extending Image Generation Functionality

*Adding a New Target Platform:* Extending Wardroom to include support for new target platforms requires the addition of a new `builder` section to Wardroom's primary Packer build file (named `packer.json`).

For target platforms that have region- or geography-specific images, additional variable files are used to provide region- or geography-specific information. AWS and Oracle Cloud (OCI) are examples of such target platforms. See the "Inputs" section below.

*Adding a New Host OS:* Adding support for additional host OSes requires adding a new `builder` section to the primary Packer build file.

*Adding a New Kubernetes Version:* So far, the generic Ansible roles called by Packer have been able to support new Kubernetes versions with little or no modifications (only requiring the user to provide a new Kubernetes version on the `packer` command line in many cases). Future releases of Kubernetes may require changes to the Ansible roles in order to add support for that release to Wardroom.

#### Extending Cluster Bootstrapping Functionality

All changes to Wardroom's cluster bootstrapping functionality require modifications to the existing Ansible roles, or the addition of new Ansible roles.

### Inputs

#### Image Generation

For image generation, Packer is the primary tool leveraged by Wardroom, so most of the inputs required by Wardroom are inputs to Packer. Some of this information is provided via variables files, others by the main build file, and users are also able to override values on the `packer` command line itself.

* _Platform credentials:_ Packer will require the appropriate credentials for the target platform (AWS, vSphere, GCP, etc.). As these vary from platform to platform, users are encouraged to refer to the Packer documentation for specific details. For security purposes, no credentials are or should be stored within Wardroom's artifacts.
* _Base image:_ Packer typically builds on top of a base image and therefore needs to know what that base image is. This information is provided via a provider- and region-specific variables files. The user can also supply this information via the `packer` command line.
* _Kubernetes version:_ A default version is supplied in the main Packer build file, but users can override that version via the `packer` command line.
* _Kubernetes CNI version:_ This is handled in the same way as the Kubernetes version.
* _Build version:_ No default build version value is defined; it must be supplied by the user on the `packer` command line.

#### Cluster Bootstrapping

For cluster bootstrapping, Ansible is the primary tool leveraged by Wardroom, so most of the inputs required by Wardroom are inputs to Ansible.

* _Instance/OS credentials:_ Ansible will need appropriate credentials to connect to the target instances/OSes and perform its configuration tasks.
* _Inventory:_ Ansible will need access to an inventory (either prepared in advance by the user or created dynamically from a source) to know which instances/OSes to orchestrate.

### Outputs

#### Image Generation

The primary output of Wardroom when used for image generation will be the creation of a platform-specific base image (such as an AMI for AWS, or an image for GCP). This image will appear within the account of the credentials supplied to Packer (as described in the Inputs section above).

#### Cluster Bootstrapping

The primary output of Wardroom when used for cluster bootstrapping will be the creation of a Kubernetes cluster. This Kubernetes cluster will be created from the inventory supplied to Ansible.

### Testing/Validation

Wardroom does not currently have a test framework in place to validate images. Two forms of testing are currently under exploration:

* Using [Molecule][3] to test the Ansible roles
* Using [`goss`][4] to perform tests against the image artifacts

## Upstream Dependencies

Wardroom is dependent on the following other projects:

* Ansible
* Packer

When testing is added to the project, Wardroom will take a dependency on the test framework(s) used.

## Downstream Dependencies

The following other projects are dependent on Wardroom or components of Wardroom:

* The [VMware AWS Quickstart][5] is dependent on Wardroom for generating the AWS AMIs that it uses.

[1]: https://www.ansible.com
[2]: https://www.packer.io
[3]: https://github.com/ansible/molecule
[4]: https://github.com/aelsabbahy/goss
[5]: https://github.com/heptio/aws-quickstart/
