"""
This module provides a custom JSON provider for Flask that handles
serialization of additional Python objects.
"""

from datetime import time
from typing import Any

from flask.json.provider import DefaultJSONProvider


class JSONProvider(DefaultJSONProvider):
    """
    Custom JSON provider for Flask that extends the default JSON provider.

    This provider adds support for serializing additional Python objects.

    Methods:
        default(obj: Any) -> Any: Override to add custom serialization logic.
    """

    def default(self, obj: Any) -> Any:
        """
        Override the default method to add custom serialization.

        Args:
            obj: The object to serialize.

        Returns:
            The serialized object or None if the object is of type `time`.
        """
        if isinstance(obj, time):
            return None
        return super().default(obj)
