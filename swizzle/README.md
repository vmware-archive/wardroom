swizzle
=======
The swizzle directory includes a playbook used to orchestrate the installation of Kubernetes by way of kubeadm. This add the ability to make kubeadm HA.

Usage
-----
Vagrant:
```
$ python provision.py
```

Ansible:
```
$ ansible-playbook -i $inventory swizzle.yml <extra ansible args>
```

This playbook make use of the baseline config management provided by the various wardoom roles. We do not use the native Vagrant ansible support (ie. `vagrant provision`) as it does not execute playbooks across all virtual machines simultaneously; only serially.
