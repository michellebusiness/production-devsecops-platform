output "vpc_id" {
  description = "ID of the platform VPC"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = module.vpc.private_subnet_ids
}

output "nat_gateway_id" {
  description = "ID of the NAT Gateway"
  value       = module.vpc.nat_gateway_id
}
output "eks_cluster_name" {
  description = "Name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "API endpoint of the EKS cluster"
  value       = module.eks.cluster_endpoint
}

output "eks_cluster_version" {
  description = "Kubernetes version used by EKS"
  value       = module.eks.cluster_version
}

output "eks_node_group_name" {
  description = "Name of the EKS managed node group"
  value       = module.eks.node_group_name
}

output "eks_cluster_role_arn" {
  description = "ARN of the EKS cluster IAM role"
  value       = module.eks.cluster_role_arn
}

output "eks_node_role_arn" {
  description = "ARN of the EKS worker node IAM role"
  value       = module.eks.node_role_arn
}
output "api_ecr_repository_url" {
  value = module.ecr.api_repository_url
}

output "worker_ecr_repository_url" {
  value = module.ecr.worker_repository_url
}
output "github_actions_role_arn" {
  description = "IAM role assumed by GitHub Actions through OIDC"
  value       = module.github_oidc.role_arn
}