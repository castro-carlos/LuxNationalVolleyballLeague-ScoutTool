variable "aws_region" {
  type        = string
  default     = "eu-central-1"
  description = "AWS region for infrastructure deployment"
}

variable "project_name" {
  type        = string
  default     = "volleyball-app"
  description = "Project name tag for resource naming"
}

variable "instance_type" {
  type        = string
  default     = "t3.micro"
  description = "EC2 instance type"
}