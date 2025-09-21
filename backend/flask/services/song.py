"""
This module provides the SongService class, which handles operations related to songs
in the application. It interacts with the database to retrieve and process song data.
"""

import json

from backend.flask.exceptions.boto import raise_http_exception
from backend.flask.services.s3 import S3Service


class SongService(S3Service):
    """
    Service class for handling operations related to songs.
    """

    @raise_http_exception
    def __init__(self, config):
        super().__init__(config)

        self.songs = json.loads(
            self._s3_client.get_object(
                Bucket=self._bucket_name, Key="songs/songs.json"
            )["Body"].read()
        )

        for song in self.songs:
            song["hash"] = self._create_hash(song)

    def get_songs(self) -> list[dict[str, str]]:
        """Get the list of songs."""
        return self.songs

    def get_song(self, song_hash: str) -> None:
        """
        Get a song by its hash.

        :param song_hash: The song_hash to get.

        Raises:
            ValueError: If the song_hash is invalid.
        """
        song = next((song for song in self.songs if song["hash"] == song_hash), None)
        if song is None:
            raise ValueError(f"Song with hash '{song_hash}' not found")

        return song
