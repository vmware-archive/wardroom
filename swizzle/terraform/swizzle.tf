variable "os" {
  default = "ubuntu-16.04"
}

variable "base_images" {
  type = "map"
  default = {
    "centos-7" = "ami-9887c6e7"
    "ubuntu-16.04" = "ami-759bc50a"
  }
}
