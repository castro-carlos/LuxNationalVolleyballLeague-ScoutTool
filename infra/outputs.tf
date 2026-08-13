output "server_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.volleyball_server.public_ip
}

output "fastapi_url" {
  description = "Direct URL to access the FastAPI backend"
  value       = "http://${aws_instance.volleyball_server.public_ip}:8000"
}