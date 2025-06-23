resource "aws_rds_cluster_parameter_group" "main" {
  name   = local.common_tags.Name
  family = "aurora-postgresql14"
  parameter {
    name  = "rds.force_ssl"
    value = 1
  }
}

resource "aws_rds_cluster" "main" {
  cluster_identifier              = local.common_tags.Name
  engine                          = "aurora-postgresql"
  # engine_version                  = "14.5"
  engine_version                  = "14.11"
  copy_tags_to_snapshot           = true
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.main.name
  db_subnet_group_name            = aws_db_subnet_group.public.name
  master_username                 = local.db_credentials["username"]
  master_password                 = local.db_credentials["password"]
  skip_final_snapshot             = true
  vpc_security_group_ids          = [aws_security_group.database.id]
  serverlessv2_scaling_configuration {
    max_capacity = 16
    min_capacity = 0.5
  }
}

resource "aws_rds_cluster_instance" "main" {
  cluster_identifier  = aws_rds_cluster.main.id
  identifier          = "${aws_rds_cluster.main.cluster_identifier}-instance"
  instance_class      = "db.serverless"
  engine              = aws_rds_cluster.main.engine
  publicly_accessible = true
}
