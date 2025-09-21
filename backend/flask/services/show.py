"""
This module provides the ShowService class, which handles operations related to shows
in the application. It interacts with the database to retrieve and process show data.
"""

import json
from datetime import datetime
from io import BytesIO

import qrcode
import qrcode.constants
from qrcode.image.base import BaseImage

from backend.flask.exceptions.boto import raise_http_exception
from backend.flask.services.s3 import S3Service


class ShowService(S3Service):
    """
    Service class for handling operations related to shows.

    Inherits from DataService to provide database interaction capabilities.
    """

    @raise_http_exception
    def __init__(self, config):
        super().__init__(config)

        self.shows = json.loads(
            self._s3_client.get_object(
                Bucket=self._bucket_name, Key="shows/shows.json"
            )["Body"].read()
        )

        for show in self.shows:
            if "hash" not in show:
                show["hash"] = self._create_hash(show)

    def get_shows(self) -> list[dict[str, str]]:
        """Get the list of shows."""
        return self.shows

    def get_show(self, show_hash: str) -> None:
        """
        Get a show by its hash.

        :param show_hash: The show_hash to get.

        Raises:
            ValueError: If the show_hash is invalid.
        """
        show = next((show for show in self.shows if show["hash"] == show_hash), None)
        if show is None:
            raise ValueError(f"Show with hash '{show_hash}' not found")

        return show

    def get_upcoming_shows(self) -> list[dict[str, str]]:
        """Get the list of upcoming shows."""
        return [
            show
            for show in self.shows
            if datetime.fromisoformat(show.get("end_time")) > datetime.now() and show.get("name") != "DEMO"
        ]

    def insert_show(self, show: dict[str, str]) -> None:
        """Insert a new show into the list."""
        show["hash"] = self._create_hash(show)
        show["url"] = (
            f"https://www.throwbackrequestlive.com/api/requests/redirect/{show['hash']}"
        )

        image = self.create_qr_code(show["url"])
        buffer = BytesIO()
        image.save(buffer)
        buffer.seek(0)

        self._s3_client.put_object(
            Bucket=self._bucket_name,
            Key=f"shows/{show['name']}-{show['venue']}-{show['start_time']}-{show['hash']}/qr.png",
            Body=buffer,
            ContentType="image/png",
        )

        self.shows.append(show)
        self._s3_client.put_object(
            Bucket=self._bucket_name,
            Key="shows/shows.json",
            Body=json.dumps(self.shows),
        )

    def create_qr_code(self, url: str) -> BaseImage:
        """
        Create a QR code for the entry point.

        :param url: The URL to encode in the QR code.

        Returns:
            str: The URL of the QR code image.
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

        buffer = BytesIO()
        img.save(buffer)
        buffer.seek(0)

        return img

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
