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
  description = "ARN of the EKS worker node IAM role"
  value       = aws_iam_role.node.arn
}

output "eks_oidc_provider_arn" {
  description = "ARN of the EKS OIDC provider used by IRSA"
  value       = aws_iam_openid_connect_provider.eks.arn
}

output "ebs_csi_addon_name" {
  description = "Name of the Amazon EBS CSI managed add-on"
  value       = aws_eks_addon.ebs_csi_driver.addon_name
}

output "ebs_csi_addon_id" {
  description = "ID of the Amazon EBS CSI managed add-on"
  value       = aws_eks_addon.ebs_csi_driver.id
}

output "ebs_csi_role_arn" {
  description = "IAM role ARN used by the EBS CSI controller"
  value       = aws_iam_role.ebs_csi.arn
}