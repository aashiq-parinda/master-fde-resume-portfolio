terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# ==============================================================================
# 1. RESOURCE GROUP & NETWORKING (VNet, delegated subnets)
# ==============================================================================

resource "azurerm_resource_group" "rg" {
  name     = "integration-platform-rg"
  location = var.location
}

resource "azurerm_virtual_network" "vnet" {
  name                = "integration-vnet"
  address_space       = var.vnet_address_space
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

# Subnet delegated for Container App Environment
resource "azurerm_subnet" "app_subnet" {
  name                 = "integration-app-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.subnet_prefixes[0]]
}

# Subnet delegated for Azure Database for PostgreSQL (Flexible Server)
resource "azurerm_subnet" "db_subnet" {
  name                 = "integration-db-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.subnet_prefixes[1]]
  service_endpoints    = ["Microsoft.Storage"]

  delegation {
    name = "postgres_delegation"
    service_delegation {
      name    = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = ["Microsoft.Network/virtualNetworks/subnets/action"]
    }
  }
}

# ==============================================================================
# 2. NETWORK SECURITY GROUPS (NSGs)
# ==============================================================================

resource "azurerm_network_security_group" "db_nsg" {
  name                = "integration-db-nsg"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  # Allow Postgres inbound only from the app subnet
  security_rule {
    name                       = "AllowPostgresFromAppSubnet"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "5432"
    source_address_prefix      = var.subnet_prefixes[0]
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "db_nsg_assoc" {
  subnet_id                 = azurerm_subnet.db_subnet.id
  network_security_group_id = azurerm_network_security_group.db_nsg.id
}

# ==============================================================================
# 3. PRIVATE DNS ZONES (Required for Azure Flexible Server within VNet)
# ==============================================================================

resource "azurerm_private_dns_zone" "dns_zone" {
  name                = "integration-postgres.private.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "vnet_dns_link" {
  name                  = "integration-vnet-dns-link"
  resource_group_name   = azurerm_resource_group.rg.name
  private_dns_zone_name = azurerm_private_dns_zone.dns_zone.name
  virtual_network_id    = azurerm_virtual_network.vnet.id
}

# ==============================================================================
# 4. DATABASE (Azure PostgreSQL Flexible Server)
# ==============================================================================

resource "azurerm_postgresql_flexible_server" "integration_postgres" {
  name                   = "integration-postgres-server"
  resource_group_name    = azurerm_resource_group.rg.name
  location               = azurerm_resource_group.rg.location
  version                = "15"
  delegated_subnet_id    = azurerm_subnet.db_subnet.id
  private_dns_zone_id    = azurerm_private_dns_zone.dns_zone.id
  administrator_login    = var.db_username
  administrator_password = var.db_password
  zone                   = "1"

  storage_mb = 32768
  sku_name   = "GP_Standard_D2s_v3" # Production scale Flexible Server SKU

  depends_on = [azurerm_private_dns_zone_virtual_network_link.vnet_dns_link]
}

# ==============================================================================
# 5. SECRETS MANAGEMENT (Azure Key Vault)
# ==============================================================================

data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "integration_kv" {
  name                        = "integration-vault-secret"
  location                    = azurerm_resource_group.rg.location
  resource_group_name         = azurerm_resource_group.rg.name
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "standard"
  purge_protection_enabled    = false

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "Get", "List", "Set", "Delete", "Purge"
    ]
  }
}

resource "azurerm_key_vault_secret" "db_host" {
  name         = "DB-HOST"
  value        = azurerm_postgresql_flexible_server.integration_postgres.fqdn
  key_vault_id = azurerm_key_vault.integration_kv.id
}

resource "azurerm_key_vault_secret" "db_password" {
  name         = "DB-PASSWORD"
  value        = var.db_password
  key_vault_id = azurerm_key_vault.integration_kv.id
}

resource "azurerm_key_vault_secret" "rest_key" {
  name         = "REST-API-KEY"
  value        = var.rest_api_key
  key_vault_id = azurerm_key_vault.integration_kv.id
}

resource "azurerm_key_vault_secret" "xml_password" {
  name         = "XML-PASSWORD"
  value        = var.xml_password
  key_vault_id = azurerm_key_vault.integration_kv.id
}

resource "azurerm_key_vault_secret" "webhook_secret" {
  name         = "WEBHOOK-SECRET"
  value        = var.webhook_secret
  key_vault_id = azurerm_key_vault.integration_kv.id
}

# ==============================================================================
# 6. CONTAINER COMPUTE (Azure Container App)
# ==============================================================================

resource "azurerm_container_app_environment" "app_env" {
  name                       = "integration-app-env"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  infrastructure_subnet_id   = azurerm_subnet.app_subnet.id
  internal_load_balancer_enabled = false
}

resource "azurerm_container_app" "integration_app" {
  name                         = "integration-engine-app"
  container_app_environment_id = azurerm_container_app_environment.app_env.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {
    container {
      name   = "integration-app"
      image  = "nginx:alpine" # Placeholder image, CI/CD replaces with build artifact
      cpu    = "0.25"
      memory = "0.5Gi"

      env {
        name  = "ENV"
        value = var.environment
      }
      env {
        name  = "DB_PORT"
        value = "5432"
      }
      env {
        name  = "DB_NAME"
        value = "postgres"
      }
      env {
        name  = "DB_USER"
        value = var.db_username
      }
      env {
        name  = "XML_SOURCE_USERNAME"
        value = var.xml_username
      }
      # Key Vault mappings
      env {
        name        = "DB_HOST"
        secret_name = "db-host"
      }
      env {
        name        = "DB_PASSWORD"
        secret_name = "db-password"
      }
      env {
        name        = "REST_SOURCE_API_KEY"
        secret_name = "rest-key"
      }
      env {
        name        = "XML_SOURCE_PASSWORD"
        secret_name = "xml-password"
      }
      env {
        name        = "WEBHOOK_SIGNATURE_KEY"
        secret_name = "webhook-secret"
      }
    }
  }

  ingress {
    allow_insecure_connections = false
    external_enabled           = true
    target_port                = 8001
    transport                  = "auto"

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  secret {
    name  = "db-host"
    value = azurerm_postgresql_flexible_server.integration_postgres.fqdn
  }
  secret {
    name  = "db-password"
    value = var.db_password
  }
  secret {
    name  = "rest-key"
    value = var.rest_api_key
  }
  secret {
    name  = "xml-password"
    value = var.xml_password
  }
  secret {
    name  = "webhook-secret"
    value = var.webhook_secret
  }
}
