output "vpc_id" {
  description = "The ID of the generated AWS VPC"
  value       = aws_vpc.main.id
}

output "database_endpoint" {
  description = "The connection endpoint for the RDS PostgreSQL DB instance"
  value       = aws_db_instance.postgres.endpoint
}

output "redis_primary_endpoint" {
  description = "The primary endpoint address for ElastiCache Redis replication group"
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
}

output "api_load_balancer_dns" {
  description = "DNS name of the public-facing application load balancer for the API"
  value       = aws_lb.api.dns_name
}
