module "k8s-vpc" {
  source = "./modules/vpc"

  name              = "k8s"
  vpc_cidr_block    = "${var.vpc_cidr}"
  vpc_dns_hostnames = "true"
  vpc_dns_support   = "true"
  subnet_map_pub_ip = "true"
}

resource "aws_security_group" "etcd_sg" {
  name        = "etcd_sg"
  description = "Allow traffic needed by etcd"
  vpc_id      = "${module.k8s-vpc.vpc_id}"
}

resource "aws_security_group_rule" "etcd_sg_allow_sg_in" {
  security_group_id        = "${aws_security_group.etcd_sg.id}"
  type                     = "ingress"
  from_port                = 0
  to_port                  = 0
  protocol                 = "-1"
  source_security_group_id = "${aws_security_group.etcd_sg.id}"
}

resource "aws_security_group_rule" "etcd_sg_allow_sg_out" {
  security_group_id        = "${aws_security_group.etcd_sg.id}"
  type                     = "egress"
  from_port                = 0
  to_port                  = 0
  protocol                 = "-1"
  source_security_group_id = "${aws_security_group.etcd_sg.id}"
}

resource "aws_security_group_rule" "etcd_sg_allow_client" {
  security_group_id = "${aws_security_group.etcd_sg.id}"
  type              = "ingress"
  from_port         = 2379
  to_port           = 2379
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "etcd_sg_allow_peer" {
  security_group_id = "${aws_security_group.etcd_sg.id}"
  type              = "ingress"
  from_port         = 2380
  to_port           = 2380
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group" "k8s_sg" {
  name        = "k8s_sg"
  description = "Allow traffic needed by Kubernetes"
  vpc_id      = "${module.k8s-vpc.vpc_id}"
}

resource "aws_security_group_rule" "k8s_sg_allow_sg_in" {
  security_group_id        = "${aws_security_group.k8s_sg.id}"
  type                     = "ingress"
  from_port                = 0
  to_port                  = 0
  protocol                 = "-1"
  source_security_group_id = "${aws_security_group.k8s_sg.id}"
}

resource "aws_security_group_rule" "k8s_sg_allow_sg_out" {
  security_group_id        = "${aws_security_group.k8s_sg.id}"
  type                     = "egress"
  from_port                = 0
  to_port                  = 0
  protocol                 = "-1"
  source_security_group_id = "${aws_security_group.k8s_sg.id}"
}

resource "aws_security_group_rule" "k8s_sg_allow_apiserver" {
  security_group_id = "${aws_security_group.k8s_sg.id}"
  type              = "ingress"
  from_port         = 6443
  to_port           = 6443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
}

module "masters" {
  source = "./modules/instance-cluster"

  name         = "master"
  ami          = "${lookup(var.base_images, var.os, "You must define var.os")}"
  type         = "${var.node_type}"
  ssh_key      = "${var.key_pair}"
  cluster_size = 3
  subnet_list  = ["${module.k8s-vpc.subnet_id}"]

  sec_group_list = ["${module.k8s-vpc.default_sg_id}", "${aws_security_group.etcd_sg.id}", "${aws_security_group.k8s_sg.id}"]

  role          = "master"
  opt_tag_name  = "environment"
  opt_tag_value = "testing"
}

module "workers" {
  source = "./modules/instance-cluster"

  name         = "worker"
  ami          = "${lookup(var.base_images, var.os, "You must define var.os")}"
  type         = "${var.node_type}"
  ssh_key      = "${var.key_pair}"
  cluster_size = 2
  subnet_list  = ["${module.k8s-vpc.subnet_id}"]

  sec_group_list = ["${module.k8s-vpc.default_sg_id}", "${aws_security_group.k8s_sg.id}"]

  role          = "worker"
  opt_tag_name  = "environment"
  opt_tag_value = "testing"
}

resource "aws_elb" "master_elb" {
  name                      = "master-elb"
  subnets                   = ["${module.k8s-vpc.subnet_id}"]
  instances                 = ["${module.masters.cluster_instance_ids}"]
  cross_zone_load_balancing = true
  security_groups           = ["${module.k8s-vpc.default_sg_id}", "${aws_security_group.k8s_sg.id}"]

  listener {
    instance_port     = 6443
    instance_protocol = "tcp"
    lb_port           = 6443
    lb_protocol       = "tcp"
  }

  health_check {
    target              = "TCP:6443"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    interval            = 10
  }

  tags {
    Name        = "master-elb"
    environment = "testing"
  }
}
