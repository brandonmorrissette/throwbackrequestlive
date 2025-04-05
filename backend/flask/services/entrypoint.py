"""
This module provides the AuthService class for handling authentication.
"""

import io
from uuid import uuid4

import boto3
import qrcode
import qrcode.constants
from qrcode.image.base import BaseImage

from backend.flask.config import Config
from backend.flask.exceptions.boto import raise_http_exception
from backend.flask.services.data import DataService


class EntryPointService(DataService):
    """
    Service for handling entry point operations.
    """

    @raise_http_exception
    def __init__(self, config: Config) -> None:
        """
        Initialize the EntryPointService.

        Args:
            config (Config): The configuration object.
        """
        super().__init__(config)

        self.s3_client = boto3.client("s3", region_name=config.AWS_DEFAULT_REGION)

        ssm_client = boto3.client("ssm", region_name=config.AWS_DEFAULT_REGION)

        self.bucket_name = ssm_client.get_parameter(
            Name=f"/{config.project_name}-{config.environment}/bucket-name",
            WithDecryption=True,
        )["Parameter"]["Value"]

    def create_entry_point(self, base_url: str) -> str:
        """
        Create an entry point.

        :param base_url: The base URL for the entry point.

        Returns:
            dict: The created entry point details.
        """
        entry_point_id = str(uuid4())
        entry_point_url = (
            f"{base_url.rstrip('/')}/entrypoint/?entryPointId={entry_point_id}"
        )
        self.create_qr_code(entry_point_url)
        self.insert_rows(
            "entry_points",
            [
                {
                    "id": entry_point_id,
                }
            ],
        )
        return entry_point_id

    def create_qr_code(self, url: str) -> BaseImage:
        """
        Create a QR code for the entry point.

        :param url: The URL to encode in the QR code.

        Returns:
            str: The URL of the QR code image.
        """

        key = f"entrypoints/{url}/qr.png"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer)
        buffer.seek(0)

        self.s3_client.put_object(
            Bucket=self,
            Key=key,
            Body=buffer,
            ContentType="image/png",
        )

        return img
