"""Various types."""

import abc
import pathlib
from typing import Optional

import attr
import packaging.specifiers
import packaging.version


@attr.s(auto_attribs=True)
class Project(abc.ABC):
    """A Python project.

    This class is meant to be subclassed by plugins and returned by the plugin's
    `reticulated_get_project`.
    """

    root: pathlib.Path = attr.ib()

    @abc.abstractmethod
    def get_direct_dependencies(self):
        """Get the project's direct dependencies (both runtime and dev)."""


class VersionSpecifier(abc.ABC):
    """A version specifier.

    Note that depending on the implementation/value one specifier might have several clauses.
        E.g. PEP 440-compliant version specifiers allow multiple comma-separated clauses.
    """

    @abc.abstractmethod
    def matches(self, version: packaging.version.Version) -> bool:
        """Return whether or not version matches this specifier.

        :param version: The version to match against.
        """


class PEP440VersionSpecifier(VersionSpecifier):
    """A PEP-440-compliant VersionSpecifier implementation."""

    def __init__(self, value) -> None:
        """Initialize the specifier.

        :raises packaging.specifiers.InvalidSpecifier: If the given value is bad.
        """
        self._specifier_set = packaging.specifiers.SpecifierSet(value)

    def matches(self, version: packaging.version.Version) -> bool:
        """Implements VersionSpecifier.matches.

        .. seealso:: :py:meth:`VersionSpecifier.matches() <VersionSpecifier.matches>`
        """
        return version in self._specifier_set


@attr.s(auto_attribs=True)
class Dependency:
    """A project dependency on another package."""

    name: str = attr.ib()
    version_spec: VersionSpecifier = attr.ib()


class VenvManager(abc.ABC):
    """Virtual environment manager."""

    @abc.abstractmethod
    def create(self, python_path: Optional[pathlib.Path]):
        """Creates a Python virtual environment."""


class InstallationManager(abc.ABC):
    """Package installation manager."""
