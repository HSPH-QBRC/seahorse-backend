data "aws_route53_zone" "main" {
  name = var.dns_zone_name
}

resource "aws_route53_record" "db" {
  name    = "${local.stack}-db"
  records = [aws_rds_cluster.main.endpoint]
  ttl     = 60
  type    = "CNAME"
  zone_id = data.aws_route53_zone.main.zone_id
}
