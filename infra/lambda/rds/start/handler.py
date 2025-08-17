"""Handler for starting an RDS instance using AWS Lambda."""

import os

import boto3


def lambda_handler(event, context):  # pylint: disable=unused-argument
    """Start the RDS instance."""
    rds_client = boto3.client("rds")
    db_instance_identifier = os.environ["DB_INSTANCE_IDENTIFIER"]
    response = rds_client.start_db_instance(DBInstanceIdentifier=db_instance_identifier)
    return {
        "response": response,
        "body": f"Starting RDS instance: {db_instance_identifier}",
    }
