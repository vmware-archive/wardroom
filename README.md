wardroom
========
A tool for creating Kubernetes-ready base operating system images. wardroom leverages Packer to build golden images of Kubernetes deploymens across a wide variety of operating systems as well as image formats.

supported operating systems
---------------------------
- Ubuntu 16.04 (Xenial)
- CentOS 7

image building
--------------
All images are built with Packer.

development
-----------
Vagrant may be used to test ansible playbook development. In this scenario, Vagrant makes use of the ansible provisioner to configure the resulting operating system image. To test all operating systems simultaneously:
```
$ vagrant up
```
You may also selectively test a single operating system as such:
```
$ vagrant up [xenial|centos7]
```

The default Vagrant provisioner is Virtualbox, but other providers are possible by way of the vagrant-mutate plugin.
