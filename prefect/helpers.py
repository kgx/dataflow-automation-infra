import base64
import json
import subprocess

import boto3
from botocore.exceptions import ClientError


def ecr_authenticate():
    ecr_client = boto3.client("ecr")

    ecr_credentials = ecr_client.get_authorization_token()["authorizationData"][0]

    ecr_username = "AWS"

    ecr_password = (
        base64.b64decode(ecr_credentials["authorizationToken"])
        .replace(b"AWS:", b"")
        .decode("utf-8")
    )

    ecr_url = ecr_credentials["proxyEndpoint"]

    subprocess.run(["docker", "login", "-u", ecr_username, "-p", ecr_password, ecr_url])


def get_prefect_token(secret_name: str):
    client = boto3.client(service_name="secretsmanager", region_name="ap-southeast-2")
    secret = None
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response["Error"]["Code"] == "DecryptionFailureException":
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InternalServiceErrorException":
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "ResourceNotFoundException":
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]
        else:
            secret = base64.b64decode(get_secret_value_response["SecretBinary"])

    return json.loads(secret).get(secret_name)


def create_ecr_repository(flow_name: str):
    """Create ECR repository for flow

    Arguments:
        flow_name {string} -- Name of the flow we are pushing

    """

    ecr_client = boto3.client(service_name="ecr")

    try:
        # Check if repository already exists
        ecr_client.describe_repositories(repositoryNames=[flow_name])
    except ClientError:
        # It will fail in case the repository doesn't exist
        try:
            # Create the ECR repository
            ecr_client.create_repository(repositoryName=flow_name)
        except ClientError as e:
            raise e
        else:
            print(f"ECR repository {flow_name} created !")
    else:
        print(f"ECR repository {flow_name} already exists !")


def __get_subnets(env: str):
    env_subnets = []
    ec2_client = boto3.client("ec2")
    subnets = ec2_client.describe_subnets()
    for subnet in subnets["Subnets"]:
        if "Tags" in subnet:
            for item in subnet["Tags"]:
                if item.get("Key") == "Name" and item.get("Value").startswith(env):
                    env_subnets.append(subnet["SubnetId"])

    return env_subnets


def __get_iam_roles(env: str):
    iam = boto3.resource("iam")
    execution_role_arn = iam.Role(f"{env}_prefect_workflow_ecs_task_execution_role").arn
    task_role_arn = iam.Role(f"{env}_prefect_workflow_ecs_task_role").arn
    return execution_role_arn, task_role_arn


def __get_aws_creds():
    aws_region = boto3.session.Session().region_name
    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]
    return account_id, aws_region


def get_aws_infrastructure(env: str):
    env_subnets = __get_subnets(env)
    execution_role_arn, task_role_arn = __get_iam_roles(env)
    account_id, aws_region = __get_aws_creds()

    return account_id, aws_region, env_subnets, execution_role_arn, task_role_arn