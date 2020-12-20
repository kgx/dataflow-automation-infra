import argparse
import os

from prefect import Client
from prefect.environments import FargateTaskEnvironment
from prefect.environments.storage import Docker

from helpers import ecr_authenticate, get_prefect_token, create_ecr_repository


def register_workflow():
    flow_module = __import__("flow")
    flow_name = flow_module.flow.name

    print(f"flow name: {flow_name}")
    print(f"env: {env}")

    flow_module.flow.environment = FargateTaskEnvironment(
        requiresCompatibilities=["FARGATE"],
        region="ap-southeast-2",
        labels=[f"{env}_dataflow_automation"],
        taskDefinition=f"{env}_{flow_name}",
        family=f"{env}_{flow_name}",
        cpu="512",
        memory="3072",
        networkMode="awsvpc",
        networkConfiguration={
            "awsvpcConfiguration": {
                "assignPublicIp": "ENABLED",
                "subnets": [
                    "subnet-05c3fcfce9275d195",
                    "subnet-02410b882477eea13",
                    "subnet-05d07984082846a2b",
                ],
                "securityGroups": [],
            }
        },
        containerDefinitions=[
            {
                "logConfiguration": {
                    "logDriver": "awslogs",
                    "options": {
                        "awslogs-region": "ap-southeast-2",
                        "awslogs-group": f"{env}_dataflow_automation_workflows",
                        "awslogs-stream-prefix": f"{env}_{flow_name}",
                    },
                }
            }
        ],
        executionRoleArn="arn:aws:iam::844814218183:role/dev_prefect_workflow_ecs_task_execution_role",
        taskRoleArn="arn:aws:iam::844814218183:role/dev_prefect_workflow_ecs_task_role",
        cluster="dev_dataflow_automation_workflows",
    )

    # Set the flow storage. Where to get the code from
    flow_module.flow.storage = Docker(
        registry_url="844814218183.dkr.ecr.ap-southeast-2.amazonaws.com",
        image_name=f"{env}_{flow_name}",
        image_tag="latest",
        python_dependencies=["boto3"],
        env_vars={"PYTHONPATH": "/opt/prefect/flows"},
    )

    # Authenticate to ECR as the registration process pushes the image to AWS
    ecr_authenticate()

    # Instantiate the prefect client
    prefect_client = Client(api_token=get_prefect_token(secret_name="prefectregistertoken"))

    # Create ECR repository
    create_ecr_repository(flow_name=f"{env}_{flow_name}")

    # Register the Workflow
    prefect_client.register(flow=flow_module.flow, project_name=f"{env}_dataflow_automation")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, required=False, default=False)

    args, unknown = parser.parse_known_args()
    env = args.env

    register_workflow()
