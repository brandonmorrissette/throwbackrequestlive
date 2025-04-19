"""
This module provides the AuthService class for handling authentication.
"""

import io
import secrets
from uuid import uuid4

import boto3
import qrcode
import qrcode.constants
import redis
from flask import current_app as app
from flask import jsonify, make_response, redirect, request, url_for
from qrcode.image.base import BaseImage
from werkzeug.wrappers.response import Response

from backend.flask.config import Config
from backend.flask.exceptions.boto import raise_http_exception
from backend.flask.services.auth import AuthService
from backend.flask.services.data import DataService


class EntryPointService(DataService, AuthService):
    """
    Service for handling entry point operations.
    """

    @raise_http_exception
    def __init__(
        self,
        redis_client: redis.Redis,
        config: Config,
    ) -> None:
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

        self._redis_client = redis_client

    def create_entrypoint(self) -> str:
        """
        Create an entry point.

        Returns:
            dict: The created entry point details.
        """
        entry_point_id = str(uuid4())
        self.insert_rows(
            "entrypoints",
            [
                {
                    "id": entry_point_id,
                }
            ],
        )
        return entry_point_id

    def create_qr_code(self, url: str, path: str | None = None) -> BaseImage:
        """
        Create a QR code for the entry point.

        :param url: The URL to encode in the QR code.

        Returns:
            str: The URL of the QR code image.
            path: The path where you wish to store the QR code image in S3.
                If None, the q3 code will not be stored.
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        if path:
            buffer = io.BytesIO()
            img.save(buffer)
            buffer.seek(0)

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"{path.rstrip('/')}/qr.png",
                Body=buffer,
                ContentType="image/png",
            )

        return img

    def start_session(self, entry_point_id: str) -> Response:
        """
        Start a session for the provided entry point ID.

        :param entry_point_id: The ID of the entry point.

        Returns:
            Response: The response object with the session details.
        """
        app.logger.info(f"Starting session for Entry point ID: {entry_point_id}")
        return self.redirect(entry_point_id)

    def validate_session(self) -> Response:
        """
        Validate the session for the provided entry point ID.
        :return: True if the session is valid, otherwise False.
        """
        access_key = request.cookies.get("accessKey", "")
        if self.validate_access_key(access_key):
            app.logger.debug(f"Access key is valid. {access_key}")
            return make_response(jsonify({"success": True}), 200)

        app.logger.debug(f"Access key is invalid. {access_key}")
        return make_response(
            jsonify(
                {
                    "success": False,
                    "error": "Invalid access key",
                    "code": 401,
                }
            ),
            401,
        )

    def redirect(self, entry_point_id: str) -> Response:
        """
        Redirect to the main page with the given UID.
        :param entry_point_id: The entry_point_id for the submission.
        :return: Redirect response to the main page.
        """
        app.logger.info(f"Redirecting Entry point ID: {entry_point_id}")
        response = make_response(redirect(url_for("renderblueprint.render_main")))

        self.set_session_cookies(response)

        return response

    def set_session_cookies(self, response: Response) -> Response:
        """
        Set cookies for the session.
        :param response: The response object to set cookies on.
        :return: The response object with default cookies set.
        """
        response.set_cookie(
            "accessKey",
            self.generate_access_key(),
            httponly=True,
            secure=True,
            samesite="Lax",
        )
        response.set_cookie(
            "uid",
            self.generate_uid(),
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        return response

    def generate_uid(self) -> str:
        """
        Generate a unique identifier (UID) for a user.
        Returns:
            str: The generated UID.
        """
        return str(uuid4())

    def generate_access_key(self) -> str:
        """
        Generate an access key.

        Returns:
            str: The generated access key.
        """
        access_key = secrets.token_urlsafe(32)
        self._redis_client.set(access_key, access_key)
        self._redis_client.expire(access_key, 600)
        return access_key

    def validate_access_key(self, access_key: str) -> bool:
        """
        Validate the access key.

        Args:
            access_key (str): The access key to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        return self._redis_client.exists(access_key) > 0
