data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "state"
    values = ["available"]
  }
}

locals {
  user_data = <<-SCRIPT
    #!/bin/bash
    set -e
    yum update -y
    yum install -y httpd
    systemctl start httpd
    systemctl enable httpd
    echo '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>IaC Challenge</title><style>body{font-family:Arial,sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;background:#f0f4f8;}h1{color:#2d3748;font-size:2rem;}</style></head><body><h1>Hi, I am ${var.owner_name} and this is my IaC</h1></body></html>' > /var/www/html/index.html
  SCRIPT
}

resource "aws_instance" "web" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [var.security_group_id]
  key_name               = var.key_name
  user_data              = local.user_data

  tags = {
    Name = "${var.prefix}-web-server"
  }
}

resource "aws_eip" "web" {
  instance = aws_instance.web.id
  domain   = "vpc"

  tags = {
    Name = "${var.prefix}-eip"
  }
}
