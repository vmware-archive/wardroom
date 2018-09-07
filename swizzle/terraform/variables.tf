variable "user_region" {
  type        = "string"
  description = "AWS region to use for all resources"
  default = "us-east-1"
}

variable "node_type" {
  type        = "string"
  description = "Type of instance to use, such as t2.large"
  default     = "t2.micro"
}

variable "key_pair" {
  type        = "string"
  description = "SSH keypair to use for accessing instances"
  default     = "ctracey"
}

variable "vpc_cidr" {
  type        = "string"
  description = "CIDR to use for the new VPC; defaults to 10.20.0.0/16"
  default     = "10.20.0.0/16"
}
