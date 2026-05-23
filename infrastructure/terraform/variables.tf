variable "gcp_project_id" {
  type        = string
  description = "Google Cloud Platform Project ID"
  default     = "securewatch-intelligent-siem"
}

variable "gcp_region" {
  type        = string
  description = "Target GCP deployment region"
  default     = "us-central1"
}
