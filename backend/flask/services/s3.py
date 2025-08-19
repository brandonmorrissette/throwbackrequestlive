"""
This module provides the S3Service class, which handles operations related to data
stored in S3.
"""

import hashlib
import json

import boto3

from backend.flask.exceptions.boto import raise_http_exception


class S3Service:
    """
    Service class for handling data stored in S3.
    """

    @raise_http_exception
    def __init__(self, config):
        ssm_client = boto3.client("ssm", region_name=config.AWS_DEFAULT_REGION)
        self._bucket_name = ssm_client.get_parameter(
            Name=f"/{config.project_name}-{config.environment}/bucket-name",
            WithDecryption=True,
        )["Parameter"]["Value"]

        self._s3_client = boto3.client("s3", region_name=config.AWS_DEFAULT_REGION)

    def _create_hash(self, _dict: dict) -> str:
        """Create a hash from dict for use as a machine-readable key."""
        dict_copy = _dict.copy()
        dict_copy.pop("hash", None)
        json_string = json.dumps(
            dict_copy,
            sort_keys=True,
            separators=(",", ":"),
        )
        hash_object = hashlib.sha256(json_string.encode("utf-8"))
        return hash_object.hexdigest()
