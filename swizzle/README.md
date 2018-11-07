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

Assumes you have machines up and ready to use for your cluster.  They need to be either Debian or Red Hat derivatives.  Nothing need be installed besides the base OS.

1. Create an inventory file and edit it to reflect your infrastructure.

    ```
    $ cp inventory.ini.example inventory.ini
    ```

2. Create an extra vars file and edit to contain the values that will work for your cluster and infrastructure.  The values contained in the example are the default values so you can delete those you don't wish to change or that don't apply to your installation.

    ```
    $ cp extra_vars.yaml.example extra_vars.yaml
    ```

3. Tell ansible where to find the roles.

    ```
    $ export ANSIBLE_ROLES_PATH=../ansible/roles
    ```

4. Run the playbook.

    ```
    $ ansible-playbook -i inventory.ini swizzle.yml --extra-vars "@extra_vars.yaml"
    ```

This playbook make use of the baseline config management provided by the various wardoom roles. We do not use the native Vagrant ansible support (ie. `vagrant provision`) as it does not execute playbooks across all virtual machines simultaneously; only serially.
