resource "random_password" "rds_master" {
  length           = 28
  special          = true
  # password for the database master user can include any printable ASCII character except /, ', ", @, or a space
  # https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Limits.html
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_secretsmanager_secret" "rds_login" {
  name = "${local.common_tags.Name}-rds"
}

resource "aws_secretsmanager_secret_version" "rds_login" {
  secret_id     = aws_secretsmanager_secret.rds_login.id
  secret_string = jsonencode({
    username = "postgres"
    password = random_password.rds_master.result
  })
}

resource "aws_rds_cluster" "main" {
  cluster_identifier     = local.common_tags.Name
  engine                 = "aurora-postgresql"
  engine_mode            = "serverless"
  engine_version         = "14.6"
  copy_tags_to_snapshot  = true
  master_username        = jsondecode(aws_secretsmanager_secret_version.rds_login.secret_string)["username"]
  master_password        = jsondecode(aws_secretsmanager_secret_version.rds_login.secret_string)["password"]
  vpc_security_group_ids = [aws_security_group.database.id]
  serverlessv2_scaling_configuration {
    max_capacity = 16
    min_capacity = 0.5
  }
}

resource "aws_rds_cluster_instance" "main" {
  cluster_identifier = aws_rds_cluster.main.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.main.engine
  engine_version     = aws_rds_cluster.main.engine_version
}
