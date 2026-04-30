# Estado de entrega

Este repositorio queda preparado para presentacion con la infraestructura definida como codigo, documentacion completa y validacion local de Terraform.

## Estado actual

Completado:

- Codigo Terraform implementado con modulos para VPC, security group y EC2.
- Backend configurado para HCP Terraform/Terraform Cloud.
- Workspace esperado: `iac-alejandro`.
- Organizacion esperada: `alejandro-iac`.
- Codigo Pulumi incluido como bonus.
- Documentacion paso a paso incluida en `IMPLEMENTACION.md`.
- Repositorio Git inicializado y publicado en GitHub.
- `terraform init` ejecutado correctamente.
- `terraform validate` ejecutado correctamente.
- `.terraform.lock.hcl` generado y versionado.

Pendiente:

- `terraform plan` y `terraform apply` requieren credenciales AWS reales en HCP Terraform.
- No se aplico infraestructura en AWS porque el usuario disponible no tiene permisos IAM para crear/ver access keys.

## Motivo del bloqueo

Al intentar usar el usuario AWS disponible se encontro una restriccion de permisos:

```text
Acceso denegado a iam:GetAccountSummary
Usuario: arn:aws:iam::721140970721:user/alejandro-pinzon
Accion: iam:GetAccountSummary
Contexto: no identity-based policy allows the action
```

Esto impide completar desde este usuario la creacion o administracion de credenciales programaticas para Terraform.

El codigo no esta bloqueado por errores de Terraform. El bloqueo es externo: falta acceso AWS con permisos suficientes.

## Datos mock incluidos

Se agrego `.env.example` con valores de ejemplo:

```text
AWS_ACCESS_KEY_ID=AKIA_MOCK_REPLACE_WITH_REAL_VALUE
AWS_SECRET_ACCESS_KEY=mock_secret_replace_with_real_value
AWS_DEFAULT_REGION=us-east-1
```

Estos valores son solo documentales. No sirven para desplegar y no deben cargarse en Terraform Cloud como credenciales reales.

## Como terminar cuando existan permisos AWS

Un administrador AWS debe entregar credenciales programaticas para un usuario o rol con permisos suficientes para crear:

- VPC.
- Internet gateway.
- Subnet.
- Route table.
- Security group.
- EC2 instance.
- Elastic IP.

Para este challenge se solicito `PowerUserAccess`.

Luego, en HCP Terraform/Terraform Cloud, configurar en el workspace `iac-alejandro` estas variables como `Environment variable`:

```text
AWS_ACCESS_KEY_ID      = valor real
AWS_SECRET_ACCESS_KEY  = valor real
AWS_DEFAULT_REGION     = us-east-1
```

Las dos credenciales deben marcarse como `Sensitive`.

Despues ejecutar:

```powershell
terraform login
terraform plan
terraform apply
```

## Evidencia esperada despues del apply

Terraform debe mostrar un output similar a:

```text
web_url = "http://<elastic-ip>"
public_ip = "<elastic-ip>"
instance_id = "i-xxxxxxxxxxxxxxxxx"
vpc_id = "vpc-xxxxxxxxxxxxxxxxx"
```

Al abrir `web_url`, la pagina debe mostrar:

```text
Hi, I am Alejandro and this is my IaC
```

## Nota para evaluacion

La solucion queda lista para ejecucion real, pero no se generaron recursos AWS porque no hay permisos disponibles para crear o administrar access keys en la cuenta AWS proporcionada.

El repositorio evita incluir credenciales reales. Los valores mock se incluyen solo para explicar el formato requerido.
