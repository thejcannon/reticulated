"""Custom exceptions raised by this package."""

import pathlib


class NoRepoException(Exception):
    """Exception raised when we weren't able to find a repository."""

    def __init__(self, path: pathlib.Path):
        """Initialize the exception, given the lookup path."""
        # @TODO: List installed plugins which implement the right hookspec
        super().__init__(f"Couldn't find a repository for path '{path}'. ")
