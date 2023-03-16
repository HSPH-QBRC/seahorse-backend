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

resource "aws_lambda_function" "hello" {
  function_name    = "hello"
  handler          = "hello.lambda_handler"
  filename         = "${path.module}/build/hello.zip"
  source_code_hash = data.archive_file.hello_zip.output_base64sha256
  runtime          = "python3.9"
  role             = aws_iam_role.lambda.arn
  environment {
    variables = {
      db_host    = aws_rds_cluster.main.endpoint
      db_name    = "postgres"
      rds_secret = aws_secretsmanager_secret.rds_login.name
    }
  }
}

data "archive_file" "hello_zip" {
  source_file = "${path.module}/src/hello.py"
  output_path = "${path.module}/build/hello.zip"
  type        = "zip"
}

# user for local development with AWS SAM CLI
resource "null_resource" "sam_metadata_aws_lambda_function_hello" {
  triggers = {
    resource_name        = "aws_lambda_function.hello"
    resource_type        = "ZIP_LAMBDA_FUNCTION"
    original_source_code = "${path.module}/src"
    built_output_path    = "${path.module}/build/hello.zip"
  }
  depends_on = [
    data.archive_file.hello_zip
  ]
}
