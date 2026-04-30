output "web_url" {
  description = "URL to access the web page"
  value       = "http://${module.ec2.public_ip}"
}

output "public_ip" {
  description = "Elastic IP of the web server"
  value       = module.ec2.public_ip
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = module.ec2.instance_id
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}
