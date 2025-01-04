from aws_cdk import Stack, RemovalPolicy
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_dynamodb as dynamodb
import aws_cdk.aws_lambda as _lambda
from aws_cdk import aws_apigateway as apigateway
from constructs import Construct


class CdkStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create S3 Bucket to store uploaded files
        self.bucket = s3.Bucket(
            self,
            "UploadedFilesBucket",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,  # Automatically delete objects when the bucket is deleted
        )

           # Create DynamoDB Table with partition and sort key
        table = dynamodb.Table(
            self, 
            "ProcessedFiles",
            partition_key=dynamodb.Attribute(
                name="file_id", 
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp", 
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY  # Automatically delete the table when the stack is deleted
        )

          # Lambda Function
        func = _lambda.Function(self, "FileProcessor",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("../lambda"),
            environment={
                "BUCKET_NAME": self.bucket.bucket_name,
                "TABLE_NAME": table.table_name
            }
        
             )

        # Grant permissions
        self.bucket.grant_read(func)
        table.grant_write_data(func)

        # API Gateway
        api = apigateway.RestApi(self, "ApiEndpoint")
        upload = api.root.add_resource("upload")
        upload.add_method("POST", apigateway.LambdaIntegration(func))
