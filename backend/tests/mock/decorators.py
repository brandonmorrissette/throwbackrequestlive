"""
This module provides a mock decorator for testing purposes.
It replaces the original decorator with a mock and traces the function calls made.
"""

from unittest.mock import MagicMock


def trace_decorator():
    """
    Creates a mock decorator that replaces the original decorator
        and traces the function calls made.

    Returns:
        tuple: A tuple containing the MagicMock object
            and a dictionary that maps function names to their arguments.
    """
    decorator_call_map = {}

    def decorator(args):
        """
        The actual decorator function that records the arguments.

        Args:
            args: The arguments passed to the decorator.

        Returns:
            function: The wrapper function.
        """

        def wrapper(f):
            """
            The wrapper function that records the function name and arguments.

            Args:
                f (function): The function being decorated.

            Returns:
                function: The original function.
            """
            decorator_call_map[f.__name__] = args
            return f

        return wrapper

    return (MagicMock(side_effect=decorator), decorator_call_map)
