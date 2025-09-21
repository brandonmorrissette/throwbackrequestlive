"""
This module provides the RequestService class, which handles operations related to requests
in the application. It interacts with the database to retrieve and process request data.
"""

import json
from collections import Counter
from io import BytesIO

from flask import current_app as app

from backend.flask.services.s3 import S3Service
from backend.flask.services.request import RequestService


class DemoService(S3Service, RequestService):
    """
    Service class for handling operations related to demo requests.
    Inherits from ShowService to provide show-related capabilities.
    """

    def __init__(self, config):
        super().__init__(config)

        self.requests = json.loads(
            self._s3_client.get_object(
                Bucket=self._bucket_name, Key="shows/DEMO/requests.json"
            )["Body"].read()
        )

    def write_request(self, song_request: dict) -> None:
        """Writes the request.

        :param request: The data for the request.
        :return: The response to the write operation.
        """
        self.requests.append(song_request)
        self._s3_client.put_object(
            Bucket=self._bucket_name,
            Key="shows/DEMO/requests.json",
            Body=json.dumps(self.requests),
        )

        app.logger.info("Request %s written successfully.", song_request["id"])



    def get_requests_counts(self) -> dict:
        """
        Get the requests for each song.
        :return: A dictionary containing song display names and their request counts.
        """
        song_counts = dict(Counter(request["display_name"] for request in self.requests))
        app.logger.info("Retrieved song request counts: %s", song_counts)
        return song_counts

    def _is_duplicate(self, request_id: str, show_hash: str) -> bool:
        """
        Check if the request is a duplicate.
        :param request_id: The unique identifier for the request.
        :param show_hash: The unique identifier for the show.
        :return: True if the request is a duplicate, otherwise False.
        """
        if any(
            request.get("id") == request_id and request.get("show_hash") == show_hash
            for request in self.requests
        ):
            app.logger.info("Duplicate request %s detected.", request_id)
            return True

        return False

    def _get_duplicate_request(self, request_id: str) -> list:
        """
        Get duplicate request by request_id.
        :param request_id: The unique identifier for the request.
        :return: JSON response with the duplicate request details.
        """
        return [
            request
            for request in self.requests
            if request.get("id") == request_id
        ]

    def get_demo_qr(self) -> BytesIO:
        """
        Retrieves the QR code image for the demo entry point.
        Returns:
            BytesIO: A BytesIO object containing the QR code image data.
        """
        response = self._s3_client.get_object(
            Bucket=self._bucket_name, Key="shows/DEMO/qr.png"
        )
        return BytesIO(response["Body"].read())
