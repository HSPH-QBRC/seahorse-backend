terraform {
  required_version = "~> 1.3.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }

  backend "s3" {
    bucket               = "seahorse-terraform"
    key                  = "backend.tfstate"
    region               = "us-east-2"
    workspace_key_prefix = "workspace"
  }
}

locals {
  stack       = lower(terraform.workspace)
  common_tags = {
    Name      = "${local.stack}-seahorse"
    Project   = "Seahorse"
    Terraform = "True"
  }
}

provider "aws" {
  region = "us-east-2"
  default_tags {
    tags = local.common_tags
  }
}
