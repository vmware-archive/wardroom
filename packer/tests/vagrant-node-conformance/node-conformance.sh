#! /bin/bash -xe

K8S_VERSION=$(< /etc/kubernetes_community_ami_version)
wget -Nq  https://dl.k8s.io/${K8S_VERSION}/kubernetes-test.tar.gz
tar -zxf kubernetes-test.tar.gz kubernetes/hack kubernetes/test kubernetes/platforms/linux/amd64
cd kubernetes/platforms/linux/amd64
sudo ./ginkgo --nodes=8 --flakeAttempts=2 --focus="\[Conformance\]" --skip="\[Flaky\]|\[Serial\]|\[sig-network\]|Container Lifecycle Hook" ./e2e_node.test -- --k8s-bin-dir=/usr/bin