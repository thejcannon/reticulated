"""Reticulated hook specifications."""

import pathlib
from typing import Optional

import pluggy

import reticulated

hookspec = pluggy.HookspecMarker("reticulated")


# @TODO: Multi-repo?
@hookspec(firstresult=True)
def reticulated_get_repo(path: pathlib.Path):
    """Finds the repository."""


# Instead of allowing projects to find projects given a directory tree, we do the walking for them
# so multiple plugins aren't duplicating the walking
@hookspec(firstresult=True)
def reticulated_get_project(path: pathlib.Path) -> Optional[reticulated.Project]:
    """Returns a project if one exists at this path, otherwise returns None.

    Returning a project stops the framework from searching deeper in this directory tree.
    """


# @TODO: Should this stop project detection? Methinks yes
@hookspec
def reticulated_ignore_project(project: reticulated.Project) -> bool:
    """Returns whether or not `project` should be ignored."""


# @TODO: Repo checking?


@hookspec
def reticulated_check_project(project):
    """Checks the project."""
