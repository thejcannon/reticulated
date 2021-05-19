"""Default hook implementations."""

import pathlib

import reticulated


@reticulated.hookimpl(trylast=True)
def reticulated_get_repo(path: pathlib.Path):
    """Return the repository given a path.

    The default implementation stops at a .git directory.
    """
    path = path.resolve()
    for parent in path.parents:
        gitdir = parent / ".git"
        if gitdir.is_dir():
            return parent

    # Hope you installed a plugin which implements this :)
    return None
