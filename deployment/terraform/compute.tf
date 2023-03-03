resource "aws_iam_role" "lambda" {
  name               = "${local.common_tags.Name}-lambda"
  description        = "Allows Seahorse Lambda functions to call AWS services on your behalf"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Sid = ""
      }
    ]
  })
}

resource "aws_lambda_function" "metadata" {
  function_name = "metadata2metadata"
  filename      = "metadata_payload.zip"
  handler       = "lambda_function.lambda_handler"
  role          = aws_iam_role.lambda.arn
  runtime       = "python3.9"
  environment {
    variables = {
      db_host    = aws_rds_cluster.main.endpoint
      db_name    = "postgres"
      rds_secret = aws_secretsmanager_secret.rds_login.name
    }
  }
}
