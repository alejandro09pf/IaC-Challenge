terraform {
  required_version = ">= 1.5.0"

  cloud {
    organization = "alejandro-iac"

    workspaces {
      name = "iac-alejandro"
    }
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
