# Guia de implementacion paso a paso

Este documento explica que se hizo en el repositorio, por que se hizo cada cosa y que pasos deben ejecutarse fuera del codigo para completar el despliegue.

## Objetivo

El objetivo del challenge es demostrar infraestructura como codigo creando en AWS una pagina web simple servida por una instancia EC2.

La infraestructura se define principalmente con Terraform y, como bonus, tambien existe una version equivalente con Pulumi.

Resultado esperado despues de aplicar Terraform:

```text
Hi, I am Alejandro and this is my IaC
```

## 1. Estructura del repositorio

Se organizo el proyecto dentro de `terraform-challenge/` con esta estructura:

```text
terraform-challenge/
  main.tf
  variables.tf
  terraform.tfvars
  versions.tf
  outputs.tf
  modules/
    vpc/
    security_group/
    ec2/
  pulumi/
  README.md
  IMPLEMENTACION.md
```

Por que se hizo asi:

- `main.tf` queda como archivo principal que conecta los modulos.
- `variables.tf` centraliza las entradas configurables.
- `terraform.tfvars` guarda valores no sensibles para este ambiente.
- `versions.tf` fija version minima de Terraform, proveedor AWS y backend de Terraform Cloud.
- `outputs.tf` muestra los valores importantes despues del despliegue.
- `modules/` separa responsabilidades para que el codigo sea mas claro y mantenible.
- `pulumi/` contiene la solucion bonus sin mezclarla con Terraform.

## 2. Configuracion de Terraform Cloud

En `versions.tf` se configuro Terraform Cloud:

```hcl
terraform {
  required_version = ">= 1.5.0"

  cloud {
    organization = "alejandro-iac"

    workspaces {
      name = "iac-alejandro"
    }
  }
}
```

Por que se hizo:

- Terraform Cloud guarda el estado remoto del despliegue.
- El estado remoto evita depender de un archivo local `terraform.tfstate`.
- El workspace `iac-alejandro` separa este challenge de otros proyectos.
- La organizacion `alejandro-iac` debe existir exactamente con ese nombre en Terraform Cloud.

Si la organizacion real tiene otro nombre, se debe cambiar esta linea:

```hcl
organization = "alejandro-iac"
```

## 3. Proveedor AWS

En `main.tf` se configuro el proveedor AWS:

```hcl
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "iac-challenge"
      Environment = var.prefix
      ManagedBy   = "terraform"
    }
  }
}
```

Por que se hizo:

- `region = var.aws_region` permite cambiar la region desde variables.
- `default_tags` agrega etiquetas comunes a los recursos creados.
- Las etiquetas ayudan a identificar recursos, costos y ownership dentro de AWS.

## 4. Variables del proyecto

En `variables.tf` se definieron valores configurables como:

```hcl
prefix
owner_name
aws_region
vpc_cidr
public_subnet_cidr
availability_zone
instance_type
key_name
```

En `terraform.tfvars` se dejaron valores por defecto del ambiente:

```hcl
prefix             = "alejandro-dev"
owner_name         = "Alejandro"
aws_region         = "us-east-1"
vpc_cidr           = "10.0.0.0/16"
public_subnet_cidr = "10.0.1.0/24"
availability_zone  = "us-east-1a"
instance_type      = "t2.micro"
```

Por que se hizo:

- Evita valores quemados directamente en los recursos.
- Facilita cambiar nombres, region o tipo de instancia sin reescribir modulos.
- Mantiene fuera del repositorio las credenciales sensibles.

Importante: las credenciales AWS no se guardan en `terraform.tfvars`. Se configuran como variables sensibles en Terraform Cloud.

## 5. Modulo VPC

El modulo `modules/vpc` crea:

- `aws_vpc`
- `aws_internet_gateway`
- `aws_subnet`
- `aws_route_table`
- `aws_route_table_association`

Por que se hizo:

- La VPC crea una red aislada para el challenge.
- El internet gateway permite salida/entrada desde internet.
- La subnet publica aloja la instancia EC2.
- La route table con ruta `0.0.0.0/0` permite trafico hacia internet.
- La asociacion conecta la subnet publica con la route table publica.

Este modulo expone:

```hcl
vpc_id
public_subnet_id
```

Esos outputs se usan despues por los modulos de security group y EC2.

## 6. Modulo Security Group

El modulo `modules/security_group` crea un security group con:

- Entrada HTTP por puerto `80`.
- Entrada SSH por puerto `22`.
- Salida libre hacia internet.

Por que se hizo:

- HTTP permite abrir la pagina web desde el navegador.
- SSH queda disponible en caso de que se quiera diagnosticar la instancia.
- Egress abierto permite que la instancia instale paquetes durante el arranque.

Nota de seguridad:

Para un ambiente real, SSH no deberia quedar abierto a `0.0.0.0/0`. Para el challenge se dejo asi por simplicidad, pero una mejora seria restringirlo a una IP especifica.

## 7. Modulo EC2

El modulo `modules/ec2` crea:

- Una AMI Amazon Linux 2 usando `data "aws_ami"`.
- Una instancia EC2.
- Un Elastic IP.
- Un script `user_data` que instala Apache y crea la pagina HTML.

Por que se hizo:

- Usar `data "aws_ami"` evita quemar un AMI ID que podria cambiar por region.
- EC2 sirve la pagina web solicitada por el challenge.
- Elastic IP entrega una IP publica estable para abrir el sitio.
- `user_data` automatiza la instalacion de Apache al iniciar la instancia.

El contenido HTML se crea con:

```bash
echo '<!DOCTYPE html>...' > /var/www/html/index.html
```

Asi la instancia queda lista sin pasos manuales despues de `terraform apply`.

## 8. Outputs

En `outputs.tf` se definieron:

```hcl
web_url
public_ip
instance_id
vpc_id
```

Por que se hizo:

- `web_url` es el dato principal para validar el challenge en el navegador.
- `public_ip` ayuda a diagnosticar conectividad.
- `instance_id` permite encontrar rapido la EC2 en AWS.
- `vpc_id` permite revisar la red creada.

## 9. Archivos ignore

Se configuro `.gitignore` para no subir archivos locales como:

```text
.terraform/
*.tfstate
*.tfstate.backup
*.tfplan
crash.log
pulumi/.venv/
pulumi/__pycache__/
pulumi/.tmp/
```

Por que se hizo:

- El estado Terraform no debe versionarse si se usa Terraform Cloud.
- Los planes y logs pueden contener informacion sensible o ruido.
- Los entornos virtuales de Python son dependencias generadas, no codigo fuente.

Tambien se agrego `.terraformignore`.

Por que se hizo:

- Terraform Cloud empaqueta y sube el directorio de trabajo.
- `.terraformignore` evita enviar carpetas pesadas o irrelevantes como `.git/`, `.terraform/` y archivos temporales.
- Esto acelera ejecuciones remotas y reduce errores por archivos locales.

## 10. Instalaciones realizadas en el PC

Como el equipo es corporativo y no se tenia administrador local, se prefirio instalar herramientas en el perfil del usuario.

Herramientas instaladas:

```text
Terraform v1.15.0
Pulumi CLI v3.225.1
Python 3.14.4
pip 26.0.1
```

Rutas usadas:

```text
C:\Users\apinzon\tools\bin\terraform.exe
C:\Users\apinzon\tools\pulumi\3.225.1\pulumi\bin\pulumi.exe
C:\Users\apinzon\AppData\Local\Programs\Python\Python314
C:\Users\apinzon\AppData\Local\Programs\Python\Python314\Scripts
```

Por que se hizo asi:

- No requiere permisos de administrador.
- Evita instalar en `Program Files`.
- Reduce choques con politicas corporativas.
- Permite desinstalar borrando carpetas del perfil si fuera necesario.

Tambien se actualizo el `PATH` de usuario para que en una terminal nueva funcionen:

```powershell
terraform version
python --version
pip --version
pulumi version
```

## 11. Particularidad con Pulumi y Python

Se intento crear un entorno virtual en:

```text
pulumi/.venv
```

Pero Python fallo al ejecutar `ensurepip` por permisos al escribir archivos temporales.

Por que pudo pasar:

- Restricciones del PC corporativo.
- Antivirus o politica de seguridad bloqueando archivos temporales `.whl`.
- Restricciones sobre `%TEMP%`.

Decision tomada:

- Se limpiaron las carpetas temporales generadas.
- Se instalaron las dependencias Pulumi en el Python de usuario.
- Se verifico que los imports funcionaran:

```powershell
python -c "import pulumi, pulumi_aws; print('pulumi imports ok')"
```

Resultado:

```text
pulumi imports ok
No broken requirements found.
```

## 12. Git local

Se inicializo Git dentro de `terraform-challenge/`.

Comandos equivalentes:

```powershell
git init
git add .
git commit -m "Add Terraform IaC challenge"
git branch -M main
```

Despues se agrego otro commit para los ignores:

```powershell
git add .gitignore .terraformignore
git commit -m "Ignore local Terraform and Pulumi artifacts"
```

Commits actuales:

```text
68e5511 Ignore local Terraform and Pulumi artifacts
959ba92 Add Terraform IaC challenge
```

Por que se hizo:

- Git deja trazabilidad de los cambios.
- La rama `main` es el estandar comun para repos nuevos en GitHub.
- Los commits separan la solucion inicial de los ajustes de higiene del repositorio.

## 13. Pasos externos pendientes

Estos pasos no se pueden completar solo desde el codigo porque requieren cuentas, tokens o aprobaciones externas.

### 13.1 AWS

1. Entrar a AWS.
2. Crear un IAM User con acceso programatico.
3. Adjuntar la policy `PowerUserAccess`.
4. Crear Access Key.
5. Guardar:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

Por que se hace:

- Terraform necesita permisos para crear VPC, subnet, security group, EC2 y Elastic IP.
- Las credenciales deben vivir fuera del repositorio.

### 13.2 Terraform Cloud

1. Entrar a `https://app.terraform.io`.
2. Crear la organizacion:

```text
alejandro-iac
```

3. Crear workspace CLI-driven:

```text
iac-alejandro
```

4. En el workspace, ir a `Variables`.
5. Agregar como `Environment variables`:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION = us-east-1
```

6. Marcar las credenciales como `Sensitive`.

Por que se hace:

- Terraform Cloud ejecuta o coordina runs usando esas credenciales.
- Guardarlas como sensitive evita exponerlas en logs o en el repositorio.

### 13.3 Login local de Terraform

Ejecutar:

```powershell
terraform login
```

Por que se hace:

- Autentica la CLI local contra Terraform Cloud.
- Permite usar el backend `cloud` configurado en `versions.tf`.

## 14. Ejecucion de Terraform

Desde la raiz del proyecto:

```powershell
cd "C:\Users\apinzon\Documents\Terraform Challenge\terraform-challenge"
terraform init
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
```

Que hace cada comando:

- `terraform init`: descarga providers y conecta con Terraform Cloud.
- `terraform fmt -recursive`: formatea todos los archivos `.tf`.
- `terraform validate`: valida sintaxis y estructura del codigo.
- `terraform plan`: muestra que recursos se van a crear antes de tocar AWS.
- `terraform apply`: crea la infraestructura en AWS.

Despues de `apply`, abrir el output:

```text
web_url
```

Ese valor debe cargar la pagina del challenge.

## 15. Publicacion en GitHub

Crear un repositorio publico vacio en GitHub y ejecutar:

```powershell
cd "C:\Users\apinzon\Documents\Terraform Challenge\terraform-challenge"
git remote add origin https://github.com/<tu-usuario>/<tu-repo>.git
git push -u origin main
```

Por que se hace:

- El challenge normalmente se entrega compartiendo un repositorio publico.
- Subir solo el codigo permite revision sin compartir credenciales ni estado local.

## 16. Bonus Pulumi

El bonus esta en:

```text
pulumi/
```

Para ejecutarlo:

```powershell
cd "C:\Users\apinzon\Documents\Terraform Challenge\terraform-challenge\pulumi"
pulumi login
pulumi stack init dev
pulumi up
```

Por que se hace:

- `pulumi login` conecta con Pulumi Cloud.
- `pulumi stack init dev` crea un stack llamado `dev`.
- `pulumi up` crea la infraestructura definida en Python.

Nota:

La version Pulumi crea recursos equivalentes a Terraform: VPC, subnet, route table, security group, EC2, Elastic IP y outputs.

## 17. Limpieza de recursos

Cuando termine la prueba, destruir recursos para evitar costos.

Terraform:

```powershell
terraform destroy
```

Pulumi:

```powershell
pulumi destroy
```

Por que se hace:

- EC2 y Elastic IP pueden generar costos.
- Destruir recursos evita gastos inesperados.
- Mantiene limpia la cuenta AWS.

## 18. Checklist final

Antes de entregar, validar:

- Terraform CLI responde con `terraform version`.
- Python responde con `python --version`.
- Pulumi responde con `pulumi version`.
- Terraform Cloud tiene organizacion `alejandro-iac`.
- Terraform Cloud tiene workspace `iac-alejandro`.
- Variables AWS estan configuradas como environment variables y sensitive.
- `terraform init` termina correctamente.
- `terraform validate` no reporta errores.
- `terraform plan` muestra recursos esperados.
- `terraform apply` termina correctamente.
- `web_url` abre la pagina.
- Repositorio GitHub publico contiene el codigo.
- No hay credenciales AWS en el repositorio.

## 19. Estado de entrega con permisos AWS pendientes

El repositorio queda listo para revision y ejecucion, pero `terraform plan` y `terraform apply` requieren credenciales AWS reales.

Durante la preparacion se confirmo que el usuario AWS disponible no tiene permisos para administrar IAM ni crear/ver access keys:

```text
Acceso denegado a iam:GetAccountSummary
Usuario: arn:aws:iam::721140970721:user/alejandro-pinzon
Accion: iam:GetAccountSummary
Contexto: no identity-based policy allows the action
```

Por ese motivo no se crearon recursos en AWS desde este usuario.

Se agregaron archivos de apoyo:

- `ESTADO_ENTREGA.md`: resume el estado actual, el bloqueo y los pasos para terminar cuando existan permisos.
- `.env.example`: muestra nombres de variables esperadas con valores mock.

Los valores mock no son credenciales reales y no deben usarse para desplegar. Solo documentan el formato que deben tener las variables en HCP Terraform.
