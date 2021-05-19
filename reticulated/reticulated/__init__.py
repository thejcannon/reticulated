"""@TODO..."""

import pluggy

from reticulated.exceptions import NoRepoException
from reticulated.types import Project


hookimpl = pluggy.HookimplMarker("reticulated")
