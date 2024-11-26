from aws_cdk import App, Stack
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_iam as iam
from constructs import Construct

from constructs import Construct

class CdkStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # *** EC2 Instance for Backend (Django) ***
        # VPC para EC2 (puedes usar la VPC predeterminada)
        vpc = ec2.Vpc(self, "VPC", max_azs=3)

        # Role para la instancia EC2
        role = iam.Role(self, "EC2Role", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        # Instancia EC2
        instance = ec2.Instance(self, "DjangoBackend",
            instance_type=ec2.InstanceType("t2.micro"),  # Puedes ajustar el tipo de instancia
            machine_image=ec2.AmazonLinuxImage(),  # Puedes cambiar esto según tu necesidad
            vpc=vpc,
            role=role,
        )

        # *** S3 Bucket for Frontend ***
        frontend_bucket = s3.Bucket(self, "FrontendBucket",
            website_index_document="index.html",  # Si tu sitio está estático
            website_error_document="error.html"
        )

        # *** API Gateway ***
        api = apigateway.RestApi(self, "DjangoAPI",
            rest_api_name="Django Service",
            description="This is a Django API Gateway"
        )

        
        hello_resource = api.root.add_resource("hello")

        
        instance_url = "http://3.130.67.167:8000"

        # Metodos ejemplo
        hello_resource.add_method("GET", apigateway.HttpIntegration(instance_url))
        