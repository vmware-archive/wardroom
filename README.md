wardroom
========
A tool for creating Kubernetes-ready base operating system images. wardroom leverages [Packer](https://github.com/hashicorp/packer) to build golden images of Kubernetes deployments across a wide variety of operating systems as well as image formats. This repo is the basis for the images used in Heptio's [aws-quickstart](https://github.com/heptio/aws-quickstart).

supported operating systems
---------------------------
- Ubuntu 16.04 (Xenial)
- CentOS 7

currently supported image formats (more to follow)
--------------------------------------------------
- AMI
- OpenStack

image building
--------------
All images are built with Packer, and configuration and details may be found in the [packer](./packer) directory.

contributing
------------
See our [contributing](CONTRIBUTING.md) guidelines and our [code of conduct](CODE-OF-CONDUCT.md). Contributions welcome by all.

swizzle
-------
The [swizzle](./swizzle) directory is a sample implementation of how one might further leverage the [ansible](https://www.ansible.com/) playbooks therein to deploy Kubernetes. As this is a proof of concept, please be aware that this code is subject to change. There is a desire to remove this code once further rigor around kubeadm HA strategies are in place.

development
-----------
[Vagrant](https://www.vagrantup.com/) may be used to test local ansible playbook development. In this scenario, Vagrant makes use of the ansible provisioner to configure the resulting operating system image. To test all operating systems simultaneously:
```
$ vagrant up
```
You may also selectively test a single operating system as such:
```
$ vagrant up [xenial|centos7]
```

To enable verbose ansible logging, you may do so by setting the `WARDROOM_DEBUG` environment variable to `'vvvv'`.

The default Vagrant provisioner is Virtualbox, but other providers are possible by way of the vagrant-mutate plugin.
