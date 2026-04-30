import pulumi
import pulumi_aws as aws

config = pulumi.Config()
prefix       = config.get("prefix")       or "alejandro-dev"
owner_name   = config.get("ownerName")   or "Alejandro"
vpc_cidr     = config.get("vpcCidr")     or "10.0.0.0/16"
subnet_cidr  = config.get("subnetCidr")  or "10.0.1.0/24"
instance_type = config.get("instanceType") or "t2.micro"

vpc = aws.ec2.Vpc(
    f"{prefix}-vpc",
    cidr_block=vpc_cidr,
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={"Name": f"{prefix}-vpc", "ManagedBy": "pulumi", "Environment": prefix},
)

igw = aws.ec2.InternetGateway(
    f"{prefix}-igw",
    vpc_id=vpc.id,
    tags={"Name": f"{prefix}-igw", "ManagedBy": "pulumi"},
)

subnet = aws.ec2.Subnet(
    f"{prefix}-public-subnet",
    vpc_id=vpc.id,
    cidr_block=subnet_cidr,
    map_public_ip_on_launch=True,
    tags={"Name": f"{prefix}-public-subnet", "ManagedBy": "pulumi"},
)

rt = aws.ec2.RouteTable(
    f"{prefix}-public-rt",
    vpc_id=vpc.id,
    routes=[aws.ec2.RouteTableRouteArgs(
        cidr_block="0.0.0.0/0",
        gateway_id=igw.id,
    )],
    tags={"Name": f"{prefix}-public-rt", "ManagedBy": "pulumi"},
)

aws.ec2.RouteTableAssociation(
    f"{prefix}-rta",
    subnet_id=subnet.id,
    route_table_id=rt.id,
)

sg = aws.ec2.SecurityGroup(
    f"{prefix}-sg-web",
    vpc_id=vpc.id,
    description="Allow HTTP and SSH inbound traffic",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            description="HTTP",
            from_port=80, to_port=80, protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            description="SSH",
            from_port=22, to_port=22, protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0, to_port=0, protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    tags={"Name": f"{prefix}-sg-web", "ManagedBy": "pulumi"},
)

ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["amazon"],
    filters=[
        aws.ec2.GetAmiFilterArgs(name="name",  values=["amzn2-ami-hvm-*-x86_64-gp2"]),
        aws.ec2.GetAmiFilterArgs(name="state", values=["available"]),
    ],
)

user_data = (
    "#!/bin/bash\n"
    "set -e\n"
    "yum update -y\n"
    "yum install -y httpd\n"
    "systemctl start httpd\n"
    "systemctl enable httpd\n"
    f'echo \'<!DOCTYPE html><html><head><meta charset="UTF-8"><title>IaC Challenge</title>'
    f'<style>body{{font-family:Arial,sans-serif;display:flex;justify-content:center;align-items:center;'
    f'height:100vh;margin:0;background:#f0f4f8;}}h1{{color:#2d3748;font-size:2rem;}}</style></head>'
    f'<body><h1>Hi, I am {owner_name} and this is my IaC</h1></body></html>\''
    f" > /var/www/html/index.html\n"
)

instance = aws.ec2.Instance(
    f"{prefix}-web-server",
    ami=ami.id,
    instance_type=instance_type,
    subnet_id=subnet.id,
    vpc_security_group_ids=[sg.id],
    user_data=user_data,
    tags={"Name": f"{prefix}-web-server", "ManagedBy": "pulumi"},
)

eip = aws.ec2.Eip(
    f"{prefix}-eip",
    instance=instance.id,
    domain="vpc",
    tags={"Name": f"{prefix}-eip", "ManagedBy": "pulumi"},
)

pulumi.export("web_url",     eip.public_ip.apply(lambda ip: f"http://{ip}"))
pulumi.export("public_ip",   eip.public_ip)
pulumi.export("instance_id", instance.id)
pulumi.export("vpc_id",      vpc.id)
