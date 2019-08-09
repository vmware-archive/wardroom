# Bootstrapping a Kubernetes Cluster

Wardroom leverages Ansible to provide orchestration around the process of bootstrapping a Kubernetes cluster with kubeadm. The Ansible playbooks and files related to this functionality can be found in the [swizzle](../swizzle) directory.

It is important to note that Wardroom does not provide infrastructure provisioning automation. Thus, all the infrastructure must be readily available before attempting to use Wardroom to bootstrap a Kubernetes cluster.

## Prerequisites

- [Ansible](http://docs.ansible.com/ansible/latest/intro_installation.html) version >= 2.4.0.0
- Nodes up and running (they are not required to be running a Wardroom-built base OS image)
- SSH Credentials

## Bootstrapping a Cluster

The following steps assume your current working directory is the `swizzle/` directory.

### Create Inventory

Create an Ansible
[inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html) file that lists all the nodes of the cluster. The following host groups are supported:

- `etcd`: List of hosts that will run etcd.
- `masters`: List of Kubernetes control planes nodes.
- `primary_master`: The first control plane node. There is nothing special about this node, other than being the node where `kubeadm init` is run. This node must also be part of the `masters` group.
- `nodes`: List of Kubernetes worker nodes.

_Note: Using Ansible's dynamic inventory feature should be possible, but it is outside of the scope of this document._ 

A sample/example inventory file can be found in the `sample-inventory.ini` file in the `swizzle/examples` directory. **This is a required step.** Without an inventory file, the Ansible playbooks used by Wardroom will not work.

#### Stacked Masters or External Etcd Cluster

Wardroom supports two etcd deployment patterns:

- _Stacked Masters_: Etcd runs on the same nodes as the Kubernetes Control Plane. To deploy stacked masters, the `etcd` host group must equal the `masters` host group.
- _External Etcd Cluster_: Etcd runs on a dedicated set of nodes. To deploy an external etcd cluster, the `etcd` host group must have no overlap with the `masters` host group.

The sample inventory file in the `swizzle/examples` directory shows an inventory for a stacked master deployment.

### Configure the Installation

The Ansible roles expose a set of variables that can be used to customize the installation to your specific environment. Most variables have defaults defined in the `defaults/` directory of each role.

To configure the installation, create an `extra-vars.yml` file to capture the variables for your environment. **This is a required step.**

Examples of an `extra-vars.yml` file are found in the `swizzle/examples` directory (both a CentOS and Ubuntu version are present).

#### Minimum Variables to Define

**At a minimum** the `extra-vars.yml` file must contain the following elements:

```yaml
---
kubernetes_common_kubeadm_config:
  networking:
    podSubnet: "192.168.0.0/16"
kubernetes_users:
- { user: ubuntu, group: ubuntu, home: /home/ubuntu }
```

The user specified in the `kubernetes_users` list should correspond to the OS being configured (use `vagrant` for local Vagrant testing). The snippet above is for Ubuntu nodes.

#### Variables for Highly-Available Clusters

When setting up a highly-available (HA) Kubernetes cluster, the control plane must be accessible through a single address. This is typically achieved by deploying a load balancer in front of the control plane nodes.

Wardroom exposes two variables to provide the load-balanced API address:

```yaml
# IP address of the load balancer fronting the Kubernetes API servers.
# This is required if an FQDN is not provided. Otherwise, this can be left empty.
kubernetes_common_api_ip: ""

# FQDN of the load balancer fronting the Kubernetes API servers.
# This variable takes precedence over the kubernetes_common_api_ip variable.
kubernetes_common_api_fqdn: ""
```

When building HA clusters with Wardroom, one of these two variables **must** be included in the `extra-vars.yml` file created to configure the installation.

#### Variables for Modifying Kubeadm Configuration

The kubeadm configuration is provided via the `kubernetes_common_kubeadm_config` variable. Wardroom provides a [default](../ansible/roles/kubernetes-common/defaults/main.yml) for this variable that
can be modified through the `extra-vars.yml` file.

Given that the variable is a hash (or map), the user-provided variable is merged with the default variable. This provides the ability to make point modifications without having to redefine the entire variable.

The following example shows how to set the pod CIDR in the `extra-vars.yml` file:

```yaml
kubernetes_common_kubeadm_config:
  networking:
    podSubnet: "192.168.0.0/16"
```

The configuration stanza shown above **must** be included in the `extra-vars.yml` file, as the default `kubeadm` configuration does not specify this value (and this value is required for most CNI plugins).

#### Modifying CNI Manifests

Wardroom provides a mechanism to modify the YAML deployment manfiests of the CNI plugin before installing it in the cluster. This mechanism is implemented as an Ansible library, which allows users to express conditions as well as modifications using JSONPath syntax.

The following example shows how to set the `CALICO_IPV4POOL_CIDR` environment variable in the Calico deployment manifests (this example would be _required_ if a user is not using the default CIDR of 192.168.0.0/16). In addition to specifying the `podSubnet` value as outlined above, users would also need to add this in the `extra-vars.yml` file:

```yaml
kubernetes_cni_calico_manifest_mods:
  - conditions:
    - expression: kind
      value: DaemonSet
    modifications:
    - expression: "spec.template.spec.containers[?(@.name == 'calico-node')].env[?(@.name == 'CALICO_IPV4POOL_CIDR')].value"
      value: "172.16.0.0/16"
```

#### Other Variables

Optionally, some other commonly-used variables that may need to be specified in the `extra-vars.yml` include:

* If the primary network interfaces is _not_ named `eth0`, then you should include `kubernetes_common_primary_interface: eth0` and `etcd_interface: eth0` in the `extra-vars.yml` file.
* The `kubernetes_cni_plugin` value is used to specify which CNI plugin to install. The default is Calico.

_Note: Wardroom sets Ansible's [hash merging behavior](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#default-hash-behaviour) to `merge`. This means that any variable that is a hash (aka. map or dictionary) with a default value will be merged with the user-provided variable._

### Run Ansible

Once you have the inventory file and the extra variables file, run the playbook:

```shell
ansible-playbook main.yml --inventory inventory.ini --extra-vars @extra-vars.yml -e wardroom_action=install
```

The value assigned to `wardroom_action` can be one of three values:

* If `install` is specified, Wardroom will bootstrap an entire cluster from scratch.
* If `add-nodes` is specified, Wardroom will add worker nodes to an existing cluster. This would allow users to bootstrap a cluster initially, then add nodes after the fact by simply updating the `nodes` group in the inventory and running Wardroom with `-e wardroom_action=add-nodes`.
* If `upgrade` is specified, Wardroom will coordinate an upgrade of the cluster to a new Kubernetes version.

## Vagrant and provision.py

Within the `swizzle` directory, Wardroom provides a Vagrantfile and the `provision.py` script _for development and testing purposes only._

The `provision.py` script generates ansible inventories from templates in the `examples/` directory.

To create a cluster using `provision.py`:

```shell
python provision.py -a install -o xenial examples/calico.yml
```

To destroy the cluster:

```shell
vagrant destroy -f
```
