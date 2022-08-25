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
        
        # Infra for Lambda function creation.
        lambdas = MainProjectStack.create_lambda_functions(
            stack=stack,
            config=config,
            env=env,
            layer=layers
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
                _lambda.Runtime.PYTHON_3_6, _lambda.Runtime.PYTHON_3_7
            ]
        )
        # requirement-layer-psycopg2 ---------------------------------------------------
        layers["requirement_layer_psycopg2"] = LambdaLayerConstruct.create_lambda_layer(
            stack=stack,
            env=env,
            config=config,
            layer_name="requirement_layer_psycopg2",
            compatible_runtimes=[
                _lambda.Runtime.PYTHON_3_6, _lambda.Runtime.PYTHON_3_7
            ]
        )
        return layers
    
    
    @staticmethod
    def create_lambda_functions(
        stack: aws_cdk.Stack,
        config: dict,
        env: str,
        layer: Dict[str, _lambda.LayerVersion] = None) -> Dict[str, _lambda.Function]:
        """Create placeholder lambda function and roles."""
        
        lambdas = {}
        
        # Lambda using Pandas
        pandas_lambdas_policy = IAMConstruct.create_managed_policy(
            stack=stack,
            env=env,
            config=config,
            policy_name="pandas_lambda",
            statements=[
                LambdaConstruct.get_cloudwatch_policy(
                    config['global']['pandas_lambdaLogsArn']
                )
            ]
        )
        pandas_lambdas_role = IAMConstruct.create_role(
            stack=stack,
            env=env,
            config=config,
            role_name="pandas_lambdas",
            assumed_by=["lambda"]   
        )
        pandas_lambdas_role.add_managed_policy(pandas_lambdas_policy)
        
        lambdas["pandas_lambda"] = LambdaConstruct.create_lambda(
            stack=stack,
            env=env,
            config=config,
            lambda_name="pandas_lambda",
            role=pandas_lambdas_role,
            duration=aws_cdk.Duration.minutes(15),
            layer=[layer["requirement_layer"]],
            memory_size=3008
        )
        
        # Lambda using psycopg2
        psycopg2_lambda_policy = IAMConstruct.create_managed_policy(
            stack=stack,
            env=env,
            config=config,
            policy_name="psycopg2_lambda",
            statements=[
                LambdaConstruct.get_cloudwatch_policy(
                    config['global']['psycopg2_lambdaLogsArn']
                )
            ]
        )
        psycopg2_lambdas_role = IAMConstruct.create_role(
            stack=stack,
            env=env,
            config=config,
            role_name="psycopg2_lambdas",
            assumed_by=["lambda"]   
        )
        psycopg2_lambdas_role.add_managed_policy(psycopg2_lambda_policy)
        
        lambdas["psycopg2_lambda"] = LambdaConstruct.create_lambda(
            stack=stack,
            env=env,
            config=config,
            lambda_name="psycopg2_lambda",
            role=psycopg2_lambdas_role,
            duration=aws_cdk.Duration.minutes(15),
            layer=[layer["requirement_layer_psycopg2"]],
            memory_size=3008
        )
        
        return lambdas