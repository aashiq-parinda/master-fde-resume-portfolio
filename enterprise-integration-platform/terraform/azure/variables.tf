variable "location" {
  type        = string
  description = "Azure deployment region location"
  default     = "East US"
}

variable "environment" {
  type        = string
  description = "Deployment environment identifier"
  default     = "production"
}

variable "vnet_address_space" {
  type        = list(string)
  description = "Address space CIDR block for the Virtual Network"
  default     = ["10.1.0.0/16"]
}

variable "subnet_prefixes" {
  type        = list(string)
  description = "Address prefixes for integration subnets (infra vs databases)"
  default     = ["10.1.1.0/24", "10.1.2.0/24"]
}

variable "db_sku_name" {
  type        = string
  description = "Azure PostgreSQL Flexible Server SKU instance size"
  default     = "Standard_B1ms"
}

variable "db_username" {
  type        = string
  description = "Database administrator username login"
  default     = "postgresadmin"
}

variable "db_password" {
  type        = string
  description = "Database administrator password login"
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
