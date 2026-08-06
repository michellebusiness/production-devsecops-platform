variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block assigned to the VPC"
  type        = string
}

variable "availability_zones" {
  description = "Availability Zones used by the VPC"
  type        = list(string)

  validation {
    condition     = length(var.availability_zones) == 2
    error_message = "Exactly two Availability Zones must be supplied."
  }
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks assigned to public subnets"
  type        = list(string)

  validation {
    condition     = length(var.public_subnet_cidrs) == 2
    error_message = "Exactly two public subnet CIDRs must be supplied."
  }
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks assigned to private subnets"
  type        = list(string)

  validation {
    condition     = length(var.private_subnet_cidrs) == 2
    error_message = "Exactly two private subnet CIDRs must be supplied."
  }
}