resource "google_compute_network" "vpc" {
  name                    = "securewatch-vpc"
  auto_create_subnetworks = "true"
}

resource "google_container_cluster" "gke" {
  name               = "securewatch-gke-cluster"
  location           = var.gcp_region
  initial_node_count = 3

  node_config {
    machine_type = "e2-standard-4" # Concurrency allocations
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }

  network = google_compute_network.vpc.name
}

resource "google_sql_database_instance" "timescaledb" {
  name             = "securewatch-timescaledb"
  database_version = "POSTGRES_15"
  region           = var.gcp_region

  settings {
    tier = "db-custom-4-16384" # Optimized Timescale resources
  }
}
