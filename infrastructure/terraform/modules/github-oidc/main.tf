locals {
  resource_prefix = "${var.project_name}-${var.environment}"

  github_oidc_subject = "repo:michellebusiness@267864506/production-devsecops-platform@1322999357:ref:refs/heads/main"
}

# GitHub Actions OIDC identity provider
resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com",
  ]

  tags = {
    Name = "${local.resource_prefix}-github-oidc"
  }
}

# Trust policy:
# Only the production-devsecops-platform repository,
# owned by michellebusiness, running from the main branch,
# may assume this IAM role.
data "aws_iam_policy_document" "github_assume_role" {
  statement {
    sid     = "AllowGitHubActionsOIDC"
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type = "Federated"

      identifiers = [
        aws_iam_openid_connect_provider.github.arn,
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"

      values = [
        "sts.amazonaws.com",
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"

      values = [
        local.github_oidc_subject,
      ]
    }
  }
}

# IAM role assumed by GitHub Actions
resource "aws_iam_role" "github_actions" {
  name               = "${local.resource_prefix}-github-actions"
  assume_role_policy = data.aws_iam_policy_document.github_assume_role.json

  tags = {
    Name = "${local.resource_prefix}-github-actions"
  }
}

# Permissions used by GitHub Actions to authenticate to ECR
# and push/pull images only from this project's repositories.
data "aws_iam_policy_document" "ecr_push" {
  statement {
    sid    = "AllowECRAuthentication"
    effect = "Allow"

    actions = [
      "ecr:GetAuthorizationToken",
    ]

    resources = ["*"]
  }

  statement {
    sid    = "AllowProjectECRPushAndPull"
    effect = "Allow"

    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "ecr:CompleteLayerUpload",
      "ecr:GetDownloadUrlForLayer",
      "ecr:GetRepositoryPolicy",
      "ecr:InitiateLayerUpload",
      "ecr:ListImages",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
    ]

    resources = var.ecr_repository_arns
  }
}

resource "aws_iam_policy" "github_actions" {
  name        = "${local.resource_prefix}-github-actions-ecr"
  description = "Allows GitHub Actions to push project images to Amazon ECR"
  policy      = data.aws_iam_policy_document.ecr_push.json

  tags = {
    Name = "${local.resource_prefix}-github-actions-ecr"
  }
}

resource "aws_iam_role_policy_attachment" "github_actions" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.github_actions.arn
}