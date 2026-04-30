provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "iac-challenge"
      Environment = var.prefix
      ManagedBy   = "terraform"
    }
  }
}

module "vpc" {
  source = "./modules/vpc"

  prefix             = var.prefix
  vpc_cidr           = var.vpc_cidr
  public_subnet_cidr = var.public_subnet_cidr
  availability_zone  = var.availability_zone
}

module "security_group" {
  source = "./modules/security_group"

  prefix = var.prefix
  vpc_id = module.vpc.vpc_id
}

module "ec2" {
  source = "./modules/ec2"

  prefix            = var.prefix
  owner_name        = var.owner_name
  subnet_id         = module.vpc.public_subnet_id
  security_group_id = module.security_group.sg_id
  instance_type     = var.instance_type
  key_name          = var.key_name
}
