locals {
  resource_prefix = "${var.project_name}-${var.environment}"
}

resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com",
  ]

  tags = {
    Name = "${local.resource_prefix}-github-oidc"
  }
}

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
        "repo:${var.github_repository}:ref:refs/heads/${var.github_branch}",
      ]
    }
  }
}

resource "aws_iam_role" "github_actions" {
  name               = "${local.resource_prefix}-github-actions"
  assume_role_policy = data.aws_iam_policy_document.github_assume_role.json

  tags = {
    Name = "${local.resource_prefix}-github-actions"
  }
}

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
    sid    = "AllowPushAndPullProjectImages"
    effect = "Allow"

    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "ecr:CompleteLayerUpload",
      "ecr:GetDownloadUrlForLayer",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
    ]

    resources = var.ecr_repository_arns
  }
}

resource "aws_iam_policy" "github_actions" {
  name   = "${local.resource_prefix}-github-actions-ecr"
  policy = data.aws_iam_policy_document.ecr_push.json

  tags = {
    Name = "${local.resource_prefix}-github-actions-ecr"
  }
}

resource "aws_iam_role_policy_attachment" "github_actions" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.github_actions.arn
}