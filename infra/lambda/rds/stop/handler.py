"""Handler for stopping an RDS instance using AWS Lambda."""

import os

import boto3


def lambda_handler(event, context):  # pylint: disable=unused-argument
    """Stops the RDS instance."""
    rds_client = boto3.client("rds")
    db_instance_identifier = os.environ["DB_INSTANCE_IDENTIFIER"]
    response = rds_client.stop_db_instance(DBInstanceIdentifier=db_instance_identifier)
    return {
        "response": response,
        "body": f"Stopping RDS instance: {db_instance_identifier}",
    }
