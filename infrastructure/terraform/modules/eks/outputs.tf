output "cluster_name" {
  description = "Name of the EKS cluster"
  value       = aws_eks_cluster.main.name
}

output "cluster_arn" {
  description = "ARN of the EKS cluster"
  value       = aws_eks_cluster.main.arn
}

output "cluster_endpoint" {
  description = "API endpoint of the EKS cluster"
  value       = aws_eks_cluster.main.endpoint
}

output "cluster_certificate_authority_data" {
  description = "Base64-encoded certificate authority data"
  value       = aws_eks_cluster.main.certificate_authority[0].data
  sensitive   = true
}

output "cluster_version" {
  description = "Kubernetes version used by EKS"
  value       = aws_eks_cluster.main.version
}

output "node_group_name" {
  description = "Name of the managed node group"
  value       = aws_eks_node_group.main.node_group_name
}

output "cluster_role_arn" {
  description = "ARN of the EKS cluster IAM role"
  value       = aws_iam_role.cluster.arn
}

output "node_role_arn" {
  description = "ARN of the EKS node IAM role"
  value       = aws_iam_role.node.arn
}