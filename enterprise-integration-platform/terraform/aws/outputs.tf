output "alb_dns_name" {
  value       = aws_lb.integration_alb.dns_name
  description = "The public DNS name of the Application Load Balancer"
}

output "rds_endpoint" {
  value       = aws_db_instance.integration_postgres.endpoint
  description = "The connection endpoint for the RDS PostgreSQL database"
}

output "ecs_cluster_name" {
  value       = aws_ecs_cluster.integration_cluster.name
  description = "The name of the deployed ECS cluster"
}

output "secrets_arn" {
  value       = aws_secretsmanager_secret.integration_secrets.arn
  description = "The ARN of the AWS Secrets Manager secret storing integration configurations"
}
