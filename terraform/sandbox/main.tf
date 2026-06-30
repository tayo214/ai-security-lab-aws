terraform {
  required_version = ">= 1.15.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = "sandbox"

  default_tags {
    tags = {
      Project     = "ai-security-lab"
      Environment = "sandbox"
      ManagedBy   = "terraform"
    }
  }
}

data "aws_caller_identity" "current" {}
