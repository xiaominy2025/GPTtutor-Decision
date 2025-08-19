#!/usr/bin/env python3
"""
AWS CDK Infrastructure for Engent Labs V1.6.6.6 Backend
Container Lambda + API Gateway with 100% feature parity
"""

import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_logs as logs,
    CfnOutput
)
from constructs import Construct

class EngentLabsBackendStack(Stack):
    """CDK Stack for Engent Labs V1.6.6.6 Backend"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ECR Repository for container images
        ecr_repository = ecr.Repository(
            self, "EngentLabsBackendRepo",
            repository_name="engent-labs-backend-v1666",
            image_scan_on_push=True,
            lifecycle_rules=[
                ecr.LifecycleRule(
                    description="Keep only 10 most recent images",
                    max_image_count=10
                )
            ]
        )

        # Lambda function from container image
        lambda_function = _lambda.Function(
            self, "EngentLabsBackendFunction",
            function_name="engent-labs-backend-v1666",
            code=_lambda.Code.from_ecr_image(
                repository=ecr_repository,
                tag_or_digest="latest"
            ),
            handler=_lambda.Handler.FROM_IMAGE,
            runtime=_lambda.Runtime.FROM_IMAGE,
            
            # Resource allocation for ML models
            memory_size=3008,  # 3GB for SentenceTransformers + FAISS + spaCy
            timeout=Duration.seconds(60),  # 60s for model loading + processing
            
            # Environment variables
            environment={
                "OPENAI_MODEL": "gpt-3.5-turbo",
                "OPENAI_MAX_TOKENS": "1000", 
                "OPENAI_TEMPERATURE": "0.3",
                # OPENAI_API_KEY will be set via AWS Secrets Manager or parameter
            },
            
            # Logging configuration
            log_retention=logs.RetentionDays.ONE_WEEK,
            
            # Architecture
            architecture=_lambda.Architecture.X86_64
        )

        # Grant Lambda permissions to access Secrets Manager for API key
        lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "secretsmanager:GetSecretValue"
                ],
                resources=[
                    f"arn:aws:secretsmanager:{self.region}:{self.account}:secret:engent-labs/*"
                ]
            )
        )

        # API Gateway HTTP API (v2) for better Lambda integration
        api = apigateway.HttpApi(
            self, "EngentLabsBackendAPI",
            api_name="engent-labs-backend-v1666",
            description="Engent Labs V1.6.6.6 Backend API with 100% feature parity",
            
            # CORS configuration
            cors_preflight=apigateway.CorsPreflightOptions(
                allow_origins=["*"],
                allow_methods=[
                    apigateway.CorsHttpMethod.GET,
                    apigateway.CorsHttpMethod.POST,
                    apigateway.CorsHttpMethod.PUT,
                    apigateway.CorsHttpMethod.OPTIONS
                ],
                allow_headers=["Content-Type", "Authorization", "Origin"],
                max_age=Duration.hours(1)
            )
        )

        # Lambda integration for API Gateway
        lambda_integration = apigateway.HttpLambdaIntegration(
            "EngentLabsBackendIntegration",
            handler=lambda_function,
            payload_format_version=apigateway.PayloadFormatVersion.VERSION_2_0
        )

        # Add routes for all V1.6.6.6 endpoints
        api.add_routes(
            path="/health",
            methods=[apigateway.HttpMethod.GET, apigateway.HttpMethod.OPTIONS],
            integration=lambda_integration
        )

        api.add_routes(
            path="/query",
            methods=[apigateway.HttpMethod.POST, apigateway.HttpMethod.OPTIONS],
            integration=lambda_integration
        )

        api.add_routes(
            path="/courses",
            methods=[apigateway.HttpMethod.GET, apigateway.HttpMethod.OPTIONS],
            integration=lambda_integration
        )

        api.add_routes(
            path="/courses/{course_id}/config",
            methods=[apigateway.HttpMethod.GET, apigateway.HttpMethod.OPTIONS],
            integration=lambda_integration
        )

        api.add_routes(
            path="/api/course/{course_id}",
            methods=[apigateway.HttpMethod.GET, apigateway.HttpMethod.OPTIONS],
            integration=lambda_integration
        )

        api.add_routes(
            path="/stats",
            methods=[apigateway.HttpMethod.GET, apigateway.HttpMethod.OPTIONS],
            integration=lambda_integration
        )

        api.add_routes(
            path="/profile",
            methods=[apigateway.HttpMethod.GET, apigateway.HttpMethod.PUT, apigateway.HttpMethod.OPTIONS],
            integration=lambda_integration
        )

        api.add_routes(
            path="/glossary",
            methods=[apigateway.HttpMethod.GET, apigateway.HttpMethod.OPTIONS],
            integration=lambda_integration
        )

        # Outputs
        CfnOutput(
            self, "ECRRepositoryURI",
            value=ecr_repository.repository_uri,
            description="ECR Repository URI for container images"
        )

        CfnOutput(
            self, "APIGatewayURL",
            value=api.url,
            description="API Gateway URL for Engent Labs V1.6.6.6 Backend"
        )

        CfnOutput(
            self, "LambdaFunctionName",
            value=lambda_function.function_name,
            description="Lambda function name"
        )

        # Store important values as instance variables for external access
        self.ecr_repository = ecr_repository
        self.lambda_function = lambda_function
        self.api_gateway = api

app = cdk.App()
EngentLabsBackendStack(app, "EngentLabsBackendStack",
    env=cdk.Environment(
        account="771049112957",  # Your AWS account ID
        region="us-east-2"       # Your preferred region
    )
)
app.synth()
