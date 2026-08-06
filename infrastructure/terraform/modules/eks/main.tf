locals {
  resource_prefix = "${var.project_name}-${var.environment}"
  cluster_name    = "${local.resource_prefix}-eks"
}

# ---------------------------------------------------
# EKS Control Plane IAM Role
# ---------------------------------------------------

data "aws_iam_policy_document" "cluster_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["eks.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "cluster" {
  name               = "${local.resource_prefix}-eks-cluster-role"
  assume_role_policy = data.aws_iam_policy_document.cluster_assume_role.json

  tags = {
    Name = "${local.resource_prefix}-eks-cluster-role"
  }
}

resource "aws_iam_role_policy_attachment" "cluster_policy" {
  role       = aws_iam_role.cluster.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

# ---------------------------------------------------
# EKS Worker Node IAM Role
# ---------------------------------------------------

data "aws_iam_policy_document" "node_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "node" {
  name               = "${local.resource_prefix}-eks-node-role"
  assume_role_policy = data.aws_iam_policy_document.node_assume_role.json

  tags = {
    Name = "${local.resource_prefix}-eks-node-role"
  }
}

resource "aws_iam_role_policy_attachment" "worker_node_policy" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_iam_role_policy_attachment" "ecr_pull_policy" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPullOnly"
}

resource "aws_iam_role_policy_attachment" "cni_policy" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

# ---------------------------------------------------
# EKS Cluster
# ---------------------------------------------------

resource "aws_eks_cluster" "main" {
  name     = local.cluster_name
  role_arn = aws_iam_role.cluster.arn
  version  = var.cluster_version

  access_config {
    authentication_mode                         = "API_AND_CONFIG_MAP"
    bootstrap_cluster_creator_admin_permissions = true
  }

  vpc_config {
    subnet_ids = var.private_subnet_ids

    endpoint_private_access = true
    endpoint_public_access  = true

    public_access_cidrs = [
      "0.0.0.0/0",
    ]
  }

  upgrade_policy {
    support_type = "STANDARD"
  }

  depends_on = [
    aws_iam_role_policy_attachment.cluster_policy,
  ]

  tags = {
    Name = local.cluster_name
  }
}

# ---------------------------------------------------
# EKS Managed Node Group
# ---------------------------------------------------

resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${local.resource_prefix}-nodes"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = var.private_subnet_ids

  version        = var.cluster_version
  instance_types = var.node_instance_types
  capacity_type  = "ON_DEMAND"
  disk_size      = 30

  scaling_config {
    desired_size = var.node_desired_size
    min_size     = var.node_min_size
    max_size     = var.node_max_size
  }

  update_config {
    max_unavailable = 1
  }

  labels = {
    environment = var.environment
    workload    = "general"
  }

  depends_on = [
    aws_iam_role_policy_attachment.worker_node_policy,
    aws_iam_role_policy_attachment.ecr_pull_policy,
    aws_iam_role_policy_attachment.cni_policy,
  ]

  tags = {
    Name = "${local.resource_prefix}-nodes"
  }
}