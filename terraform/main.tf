terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.1.0"
    }
  }
}

provider "local" {}

resource "local_file" "local_infrastructure_mock" {
  filename = "${path.module}/infrastructure_state.txt"
  content  = <<EOT
Offline Infrastructure Mock State:
----------------------------------
Environment: Development
Database: Local Docker PostgreSQL
Backend: Local Docker FastAPI
Frontend: Local Docker React/Vite

Since "All offline" was requested, this Terraform template simulates the creation
of local resources. In a real cloud setup, we would configure AWS/GCP/Azure resources here.
EOT
}
