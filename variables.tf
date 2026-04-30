variable "prefix" {
  type        = string
  description = "Unique prefix applied to all resource names and tags. Change this single value to deploy a completely new isolated environment without overwriting the previous one."
  default     = "alejandro-dev"
}

variable "owner_name" {
  type        = string
  description = "Name shown on the web page"
  default     = "Alejandro"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  type    = string
  default = "10.0.1.0/24"
}

variable "availability_zone" {
  type    = string
  default = "us-east-1a"
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}

variable "key_name" {
  type        = string
  description = "Optional EC2 key pair name for SSH access"
  default     = null
}
