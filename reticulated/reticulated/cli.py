"""CLI entrypoint definitions."""

import functools
import os
import pathlib

import click
import pluggy

import cached_property
import reticulated.exceptions
import reticulated.hookimpls
import reticulated.hookspecs


class _PathlibPath(click.Path):
    """A Click path argument that returns a pathlib.Path, not a string.

    Use this class as the type param to a click.Option or click.Argument.
    """

    def convert(self, value, param, ctx) -> pathlib.Path:
        """Extend click.Path.convert and convert the str to a pathlib.Path."""
        return pathlib.Path(super().convert(value, param, ctx))


class Main:
    """Programmatic CLI type.

    Use this if you find yourself needing to execute the CLI programmatically (from Python).
    """

    def __init__(self, path: pathlib.Path = pathlib.Path(".")):
        """Initialize Main."""
        plugin_manager = pluggy.PluginManager("reticulated")
        plugin_manager.add_hookspecs(reticulated.hookspecs)
        plugin_manager.load_setuptools_entrypoints("reticulated")
        plugin_manager.register(reticulated.hookimpls)

        self.plugin_manager = plugin_manager
        self.path = path

    @cached_property.cached_property
    def repo(self):
        """The repository to run the tool on."""
        repo = self.plugin_manager.hook.reticulated_get_repo(path=self.path)

        if repo is None:
            raise reticulated.exceptions.NoRepoException(self.path)

        return repo

    def yield_projects(self):
        """Yields projects to run the tool on."""
        yield from self._find_projects(self.repo)

    @cached_property.cached_property
    def projects(self):
        """The projects to run the tool on."""
        return list(self.yield_projects())

    def check(self):
        """Check the repository.

        @TODO: Args
        """
        for project in self.projects:
            project.check()

    def build(self):
        """Build the repository."""
        pass

    def test(self):
        """Test the repository."""
        pass

    def _find_projects(self, path: pathlib.Path):
        """Recursively traverses path looking for projects and yields them."""
        # @TODO: Filtering
        with os.scandir(path) as dir_entries:
            for entry in dir_entries:
                if entry.is_dir():
                    entry_path = pathlib.Path(entry.path)
                    project = self.plugin_manager.hook.reticulated_get_project(path=entry_path)
                    if project is not None:
                        should_ignore = any(
                            self.plugin_manager.hook.reticulated_ignore_project(project=project)
                        )
                        if not should_ignore:
                            yield project
                    else:
                        yield from self._find_projects(entry_path)


@click.group()
@click.option("--path", type=_PathlibPath(dir_okay=True))
@click.pass_context
def main(ctx, path: pathlib.Path):
    """Main entrypoint."""
    ctx.ensure_object(type(None))
    ctx.obj = Main()


@main.command()
@click.pass_obj
def check(obj):
    """Check the repo."""
    obj.check()


@main.command()
@click.pass_obj
def test(obj):
    """Test the repo."""
    obj.test()


@main.command()
@click.pass_obj
def build(obj):
    """Build all projects in the repository, in dependency-order."""
    # @TODO: Parallelization
    # @TODO: Publish
    obj.build()
