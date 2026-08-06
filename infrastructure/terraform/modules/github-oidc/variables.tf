variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "github_repository" {
  description = "GitHub repository in owner/repository format"
  type        = string
}

variable "github_branch" {
  description = "GitHub branch allowed to assume the AWS role"
  type        = string
  default     = "main"
}

variable "ecr_repository_arns" {
  description = "ECR repository ARNs that GitHub Actions can push to"
  type        = list(string)
}