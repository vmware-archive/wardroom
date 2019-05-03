# Bootstrapping a Kubernetes Cluster

Wardroom leverages Ansible to provide orchestration around the process of bootstrapping a
Kubernetes cluster with kubeadm. The Ansible playbooks and files related to this functionality can
be found in the [swizzle](../swizzle) directory.

It is important to note that Wardroom does not provide infrastructure provisioning automation.
Thus, all the infrastructure must be readily available before attempting to use Wardroom to
bootstrap a Kubernetes cluster.

## Prerequisites

- [Ansible](http://docs.ansible.com/ansible/latest/intro_installation.html) version >= 2.4.0.0
- Nodes up and running (they are not required to be running a Wardroom-built base OS image)
- SSH Credentials

## Bootstrapping a Cluster

The following steps assume your current working directory is the `swizzle/` directory.

### Create Inventory

Create an Ansible
[inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html) file that
lists all the nodes of the cluster. The following host groups are supported:

- `etcd`: List of hosts that will run etcd.
- `masters`: List of Kubernetes control planes nodes.
- `primary_master`: The first control plane node. There is nothing special about this node, other
  than being the node where `kubeadm init` is run. This node must also be part of the `masters`
  group.
- `nodes`: List of Kubernetes worker nodes.

_Note: Using Ansible's dynamic inventory feature should be possible, but it is outside of the scope of
this document._ 

#### Stacked Masters or External Etcd Cluster

Wardroom supports two etcd deployment patterns:

- _Stacked Masters_: Etcd runs on the same nodes as the Kubernetes Control Plane. To deploy stacked
  masters, the `etcd` host group must equal the `masters` host group.
- _External Etcd Cluster_: Etcd runs on a dedicated set of nodes. To deploy an external etcd
  cluster, the `etcd` host group must have no overlap with the `masters` host group.

### Configure the Installation

The Ansible roles expose a set of variables that can be used to customize the installation to your
specific environment. Most variables have defaults defined in the `defaults/` directory of each
role.

To configure the installation, create an `extra_vars.yml` file to capture the variables for your
environment. The following is a sample that includes commonly used variables:

```yaml
etcd_interface: eth0 # Interface that etcd should bind
kubernetes_common_primary_interface: eth0 # Interface that should be used to obtain the node's IP
kubernetes_cni_plugin: calico # The CNI plugin to use
```

_Note: Wardroom sets Ansible's [hash merging behavior](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#default-hash-behaviour)
to `merge`. This means that any variable that is a hash (aka. map or dictionary) with a default
value will be merged with the user-provided variable._

#### Kubernetes API IP or FQDN

When setting up a highly-available Kubernetes cluster, the control plane must be accessible through
a single address. This is typically achieved by deploying a load balancer in front of the control
plane nodes.

Wardroom exposes two variables to provide the load-balanced API address:

```yaml
# IP address of the load balancer fronting the Kubernetes API servers.
# This is required if an FQDN is not provided. Otherwise, this can be left empty.
kubernetes_common_api_ip: ""

# FQDN of the load balancer fronting the Kubernetes API servers.
# This variable takes precedence over the kubernetes_common_api_ip variable.
kubernetes_common_api_fqdn: ""
```

#### Modifying Kubeadm Configuration

The kubeadm configuration is provided via the `kubernetes_common_kubeadm_config` variable. Wardroom
provides a [default](../ansible/roles/kubernetes-common/defaults/main.yml) for this variable that
can be modified through the `extra_vars.yml` file.

Given that the variable is a hash (or map), the user-provided variable is merged with the default
variable. This provides the ability to make point modifications without having to redefine the
entire variable.

The following example shows how to set the pod CIDR in the `extra_vars.yml` file:

```yaml
kubernetes_common_kubeadm_config:
  networking:
    podSubnet: "172.16.0.0/16"
```

#### Modifying CNI Manifests

Wardroom provides a mechanism to modify the YAML deployment manfiests of the CNI plugin before
installing it in the cluster.

The following example shows how to set the `CALICO_IPV4POOL_CIDR` environment variable in the
Calico deployment manifests. This must be defined in the `extra_vars.yml` file:

```yaml
kubernetes_cni_calico_manifest_mods:
  - conditions:
    - expression: kind
      value: DaemonSet
    modifications:
    - expression: "spec.template.spec.containers[?(@.name == 'calico-node')].env[?(@.name == 'CALICO_IPV4POOL_CIDR')].value"
      value: "172.16.0.0/16"
```

### Run Ansible

Once you have the inventory and extra variables files, run the playbook:

```shell
ansible-playbook install.yml --inventory inventory.ini --extra-vars @extra_vars.yml
```

## Vagrant and provision.py

Within the `swizzle` directory, Wardroom provides a Vagrantfile and the `provision.py` script for
development and testing purposes.

The `provision.py` script generates ansible extra variables from templates in the `examples/` directory.

To create a cluster using `provision.py`:

```shell
python provision.py -a install -o xenial examples/calico.yml
```

To destroy the cluster:

```shell
vagrant destroy -f
```