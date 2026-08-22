variable "aws_region" {
  type        = string
  description = "AWS deployment region"
  default     = "us-east-1"
}

variable "environment" {
  type        = string
  description = "Deployment environment identifier"
  default     = "production"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the custom integration VPC"
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  type        = list(string)
  description = "CIDR blocks for public subnets (ALB & NAT Gateway)"
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  type        = list(string)
  description = "CIDR blocks for private subnets (ECS tasks & RDS)"
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "db_instance_class" {
  type        = string
  description = "RDS database instance size"
  default     = "db.t4g.micro"
}

variable "db_username" {
  type        = string
  description = "Database master administrator username"
  default     = "postgres"
}

variable "db_password" {
  type        = string
  description = "Database master administrator password"
  sensitive   = true
}

variable "rest_api_key" {
  type        = string
  description = "API key for legacy REST service"
  sensitive   = true
}

variable "xml_username" {
  type        = string
  description = "Username for XML basic authentication"
  default     = "admin"
}

variable "xml_password" {
  type        = string
  description = "Password for XML basic authentication"
  sensitive   = true
}

variable "webhook_secret" {
  type        = string
  description = "HMAC secret signature key for webhooks"
  sensitive   = true
}
