# IaC Challenge

Terraform project that creates a small AWS web environment:

- VPC with a public subnet and internet gateway.
- Security group allowing HTTP and SSH.
- EC2 instance running Apache.
- Elastic IP.
- Output with the public web URL.

The web page rendered by the instance says:

```text
Hi, I am Alejandro and this is my IaC
```

## Requirements

- AWS account.
- Terraform Cloud account.
- Terraform CLI installed locally.
- Git installed locally.

The Terraform Cloud backend is configured with:

```hcl
organization = "alejandro-iac"
workspace    = "iac-alejandro"
```

If your Terraform Cloud organization has a different name, update `versions.tf` before running `terraform init`.

## Terraform Cloud Setup

1. Create a Terraform Cloud account at <https://app.terraform.io>.
2. Create an organization named `alejandro-iac`.
3. Create a workspace named `iac-alejandro`.
4. Choose the `CLI-driven workflow` option.
5. In the workspace, go to `Variables`.
6. Add these as `Environment variables`:

```text
AWS_ACCESS_KEY_ID      = your AWS access key
AWS_SECRET_ACCESS_KEY  = your AWS secret key
AWS_DEFAULT_REGION     = us-east-1
```

Mark the AWS keys as `Sensitive`.

## AWS Setup

1. Create or use an AWS account.
2. Create an IAM user with programmatic access.
3. Attach the `PowerUserAccess` policy.
4. Save the Access Key ID and Secret Access Key.
5. Add those credentials to the Terraform Cloud workspace variables.

Do not commit AWS credentials to this repository.

## Run Terraform

From this directory:

```powershell
terraform login
terraform init
terraform plan
terraform apply
```

After `apply`, Terraform prints `web_url`. Open that URL in a browser to verify the deployed page.

To destroy the AWS resources later:

```powershell
terraform destroy
```

## GitHub

Initialize Git and push the project:

```powershell
git init
git add .
git commit -m "Add Terraform IaC challenge"
git branch -M main
git remote add origin https://github.com/<your-user>/<your-repo>.git
git push -u origin main
```

## Pulumi Bonus

Pulumi implementation lives in `pulumi/`.

After installing Python and Pulumi:

```powershell
cd pulumi
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pulumi login
pulumi stack init dev
pulumi up
```

To remove Pulumi-created resources:

```powershell
pulumi destroy
```
