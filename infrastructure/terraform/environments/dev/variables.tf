variable "project_name" {
  description = "Name used as a prefix for project resources"
  type        = string
  default     = "production-devsecops-platform"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region used for the infrastructure"
  type        = string
  default     = "eu-central-1"
}

variable "aws_profile" {
  description = "Local AWS CLI profile used by Terraform"
  type        = string
  default     = "default"
}

variable "vpc_cidr" {
  description = "CIDR block assigned to the VPC"
  type        = string
  default     = "10.20.0.0/16"
}

variable "availability_zones" {
  description = "Availability Zones used by the platform"
  type        = list(string)

  default = [
    "eu-central-1a",
    "eu-central-1b",
  ]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks assigned to public subnets"
  type        = list(string)

  default = [
    "10.20.1.0/24",
    "10.20.2.0/24",
  ]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks assigned to private subnets"
  type        = list(string)

  default = [
    "10.20.11.0/24",
    "10.20.12.0/24",
  ]
}
variable "eks_cluster_version" {
  description = "Kubernetes version used by Amazon EKS"
  type        = string
  default     = "1.35"
}

variable "eks_node_instance_types" {
  description = "EC2 instance types used by EKS worker nodes"
  type        = list(string)
  default     = ["t3.small"]
}

variable "eks_node_desired_size" {
  description = "Desired number of EKS worker nodes"
  type        = number
  default     = 2
}

variable "eks_node_min_size" {
  description = "Minimum number of EKS worker nodes"
  type        = number
  default     = 2
}

variable "eks_node_max_size" {
  description = "Maximum number of EKS worker nodes"
  type        = number
  default     = 3
}