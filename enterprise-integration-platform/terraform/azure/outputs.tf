output "container_app_url" {
  value       = azurerm_container_app.integration_app.ingress[0].fqdn
  description = "The fully qualified domain name of the Azure Container App"
}

output "postgresql_fqdn" {
  value       = azurerm_postgresql_flexible_server.integration_postgres.fqdn
  description = "The fully qualified domain name (endpoint) of the PostgreSQL Flexible Server"
}

output "key_vault_uri" {
  value       = azurerm_key_vault.integration_kv.vault_uri
  description = "The URI of the Azure Key Vault storing secret strings"
}
