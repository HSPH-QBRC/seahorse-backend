terraform {
  required_version = "~> 1.3.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4"
    }
  }

  backend "s3" {
    bucket               = "seahorse-terraform"
    key                  = "backend.tfstate"
    region               = "us-east-2"
    workspace_key_prefix = "workspace"
  }
}

resource "random_password" "rds_master" {
  length           = 28
  special          = true
  # password for the database master user can include any printable ASCII character except /, ', ", @, or a space
  # https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Limits.html
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_secretsmanager_secret" "rds_login" {
  name                    = "${local.common_tags.Name}-rds-credentials"
  description             = "Seahorse database master username and password"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "rds_login" {
  secret_id     = aws_secretsmanager_secret.rds_login.id
  secret_string = jsonencode({
    username = "postgres"
    password = random_password.rds_master.result
  })
}

locals {
  stack       = lower(terraform.workspace)
  common_tags = {
    Name      = "${local.stack}-seahorse"
    Project   = "Seahorse"
    Terraform = "True"
  }
  db_credentials = jsondecode(aws_secretsmanager_secret_version.rds_login.secret_string)
}

provider "aws" {
  region = "us-east-2"
  default_tags {
    tags = local.common_tags
  }
}

data "aws_region" "current" {}
