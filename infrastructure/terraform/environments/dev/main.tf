module "vpc" {
  source = "../../modules/vpc"

  project_name = var.project_name
  environment  = var.environment

  vpc_cidr             = var.vpc_cidr
  availability_zones   = var.availability_zones
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
}
module "eks" {
  source = "../../modules/eks"

  project_name = var.project_name
  environment  = var.environment

  private_subnet_ids = module.vpc.private_subnet_ids

  cluster_version     = var.eks_cluster_version
  node_instance_types = var.eks_node_instance_types

  node_desired_size = var.eks_node_desired_size
  node_min_size     = var.eks_node_min_size
  node_max_size     = var.eks_node_max_size
}