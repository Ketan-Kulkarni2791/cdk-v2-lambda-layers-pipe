"""Main python file_key for adding resources to the application stack."""
import aws_cdk
from constructs import Construct
import aws_cdk.aws_lambda as _lambda
from typing import Dict, Any

from .lambda_layer_construct import LambdaLayerConstruct
from .iam_construct import IAMConstruct
from .lambda_construct import LambdaConstruct


class MainProjectStack(aws_cdk.Stack):
    """Build the app stacks and its resources."""
    def __init__(self, env_var: str, scope: Construct, 
                 app_id: str, config: dict, **kwargs: Dict[str, Any]) -> None:
        """Creates the cloudformation templates for the projects."""
        super().__init__(scope, app_id, **kwargs)
        self.env_var = env_var
        self.config = config
        MainProjectStack.create_stack(self, self.env_var, config=config)
        
    @staticmethod
    def create_stack(stack: aws_cdk.Stack, env: str, config: dict) -> None:
        """Create and add the resources to the application stack"""
        
        # Infra for Lambda Layers
        layers = MainProjectStack.create_layers_for_lambdas(
            stack=stack,
            config=config,
            env=env
        )
    
        
    @staticmethod
    def create_layers_for_lambdas(
        stack: aws_cdk.Stack,
        config: dict,
        env: str
    ) -> Dict[str, _lambda.LayerVersion]:
        """Method to create layers."""
        
        layers = {}
        # requirement-layer-pandas ---------------------------------------------------
        layers["requirement_layer"] = LambdaLayerConstruct.create_lambda_layer(
            stack=stack,
            env=env,
            config=config,
            layer_name="requirement_layer",
            compatible_runtimes=[
                _lambda.Runtime.PYTHON_3_8, _lambda.Runtime.PYTHON_3_9
            ]
        )
        # requirement-layer-psycopg2 ---------------------------------------------------
        layers["requirement_layer_psycopg2"] = LambdaLayerConstruct.create_lambda_layer(
            stack=stack,
            env=env,
            config=config,
            layer_name="requirement_layer_psycopg2",
            compatible_runtimes=[
                _lambda.Runtime.PYTHON_3_8, _lambda.Runtime.PYTHON_3_9
            ]
        )
        return layers