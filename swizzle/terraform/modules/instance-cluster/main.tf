# Define a map for assigning tags
locals {
  common_tags = "${map(
    "${var.opt_tag_name}", "${var.opt_tag_value}",
    "role", "${var.role}"
  )}"
}

# Launch a cluster of instances
resource "aws_instance" "instance" {
  count                       = "${var.cluster_size}"
  ami                         = "${var.ami}"
  instance_type               = "${var.type}"
  subnet_id                   = "${element(var.subnet_list, count.index)}"
  key_name                    = "${var.ssh_key}"
  associate_public_ip_address = "${var.assign_pub_ip}"
  vpc_security_group_ids      = ["${var.sec_group_list}"]
  iam_instance_profile        = "${var.instance_profile}"

  tags = "${merge(
    local.common_tags,
    map(
      "Name", "${var.name}-${count.index+1}"
    )
  )}"
}
