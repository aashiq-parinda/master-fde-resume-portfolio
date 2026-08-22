variable "aws_region" {
  type        = string
  description = "AWS region to deploy resources"
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Name of the project"
  default     = "predictive-maintenance"
}

variable "environment" {
  type        = string
  description = "Target deployment environment (e.g. dev, prod)"
  default     = "production"
}

variable "db_password" {
  type        = string
  description = "Password for the RDS database application user"
  sensitive   = true
}

variable "gemini_api_key" {
  type        = string
  description = "API key for Google Gemini AI assistant"
  sensitive   = true
}
