# wardroom

Wardroom provides tooling that helps simplify the deployment of a Kubernetes cluster. More
specifically, Wardroom provides the following functionality:

* **Image Building**: Building of Kubernetes-ready base operating system images using Packer and Ansible.
* **Deployment Orchestration**: Ansible-based orchestration to deploy highly-available Kubernetes
  clusters using kubeadm.

Both use cases share a common set of [Ansible](https://github.com/ansible/ansible) roles that can
be found in the [ansible](./ansible) directory.

## Image Building

Wardroom leverages [Packer](https://github.com/hashicorp/packer) to build golden images of
Kubernetes deployments across a wide variety of operating systems as well as image formats. During
the build phase, Wardroom leverages [Ansible](https://github.com/ansible/ansible) to configure the
base operating system and produce the Kubernetes-ready golden image.

This functionality is used to create base images for the Heptio
[aws-quickstart](https://github.com/heptio/aws-quickstart).

### Supported Image Formats

* AMI

### Supported Operating Systems

* Ubuntu 16.04 (Xenial)
* Ubuntu 18.04 (Bionic)
* CentOS 7

## Deployment Orchestration

The [swizzle](./swizzle) directory contains an Ansible playbook that can be used to orchestrate the
deployment of a Kubernetes cluster using kubeadm.

## Documentation

Documentation and usage information can be found in the [docs](./docs) directory.

## Contributing

See our [contributing](CONTRIBUTING.md) guidelines and our [code of conduct](CODE-OF-CONDUCT.md).
Contributions welcome by all.

## Development

[Vagrant](https://www.vagrantup.com/) may be used to test local ansible playbook development. In this scenario, Vagrant makes use of the ansible provisioner to configure the resulting operating system image. To test all operating systems simultaneously:

``` bash
vagrant up
```

You may also selectively test a single operating system as such:

``` bash
vagrant up [xenial|bionic|centos7]
```

To enable verbose ansible logging, you may do so by setting the `WARDROOM_DEBUG` environment variable to `'vvvv'`.

The default Vagrant provisioner is Virtualbox, but other providers are possible by way of the vagrant-mutate plugin.
