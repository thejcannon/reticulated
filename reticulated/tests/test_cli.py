import pathlib

import pytest

import reticulated
import reticulated.cli


class DummyProject(reticulated.Project):
    def get_direct_dependencies(self):
        assert False


@pytest.fixture
def tmp_repo(tmp_hookimpl, tmp_path):
    """Fixture which configures a temporary path as the repo."""

    @tmp_hookimpl
    def reticulated_get_repo(path):
        return tmp_path

    return tmp_path


@pytest.fixture
def default_repo(tmp_repo):
    """tmp_repo with some files/dirs already created."""

    (tmp_repo / "project1" / "child").mkdir(parents=True)
    (tmp_repo / "project1" / "python.project").touch()
    (tmp_repo / "project1" / "child" / "python.project").touch()
    (tmp_repo / "subdir" / "project2").mkdir(parents=True)
    (tmp_repo / "subdir" / "project2" / "python.project").touch()
    (tmp_repo / "subdir" / "project2" / "IGNOREME").touch()

    return tmp_repo


def test_repo__no_repo__errors(mocker):
    main = reticulated.cli.Main()

    mocker.patch.object(main.plugin_manager.hook, "reticulated_get_repo", return_value=None)

    with pytest.raises(reticulated.NoRepoException):
        main.repo


def test_rep__default_repo_is_git_root():
    assert reticulated.cli.Main().repo == pathlib.Path(__file__).parent.parent.parent


def test_repo__single_hookimpl__respects_return_value(tmp_hookimpl):
    @tmp_hookimpl
    def reticulated_get_repo(path):
        return pathlib.Path("./CheeseShop")

    assert reticulated.cli.Main().repo == pathlib.Path("./CheeseShop")


def test_repo__multiple_hookimpls__last_one_wins(tmp_hookimpl):
    @tmp_hookimpl("Plugin1")
    def reticulated_get_repo(path):
        return pathlib.Path("./CheeseShop1")

    @tmp_hookimpl("Plugin2")  # noqa: F811
    def reticulated_get_repo(path):
        return pathlib.Path("./CheeseShop2")

    assert reticulated.cli.Main().repo == pathlib.Path("./CheeseShop2")


def test_projects__empty_dir__plugin_never_called(tmp_hookimpl, tmp_repo):
    @tmp_hookimpl
    def reticulated_get_project(path):
        assert False

    assert reticulated.cli.Main(tmp_repo).projects == []


def test_projects__doesnt_call_plugin_for_files(tmp_hookimpl, default_repo):
    @tmp_hookimpl
    def reticulated_get_project(path):
        assert not path.is_file()

    assert reticulated.cli.Main(tmp_repo).projects == []


def test_projects__doesnt_recurse_under_project(tmp_hookimpl, default_repo):
    paths = []

    @tmp_hookimpl
    def reticulated_get_project(path):
        paths.append(path)
        if (path / "python.project").is_file():
            return DummyProject(path)

    reticulated.cli.Main(default_repo).projects
    assert (default_repo / "project1" / "child") not in paths


def test_projects__multiple_projects_different_levels(tmp_hookimpl, default_repo):
    @tmp_hookimpl
    def reticulated_get_project(path):
        if (path / "python.project").is_file():
            return DummyProject(path)

    assert reticulated.cli.Main(default_repo).projects == [
        DummyProject(default_repo / "project1"),
        DummyProject(default_repo / "subdir" / "project2"),
    ]


def test_projects__multiple_project_impls(tmp_hookimpl, default_repo):
    @tmp_hookimpl("plugin1")
    def reticulated_get_project(path):
        if path.stem == "project1":
            return DummyProject(path)

    @tmp_hookimpl("plugin2")  # noqa: F811
    def reticulated_get_project(path):
        if path.stem == "project2":
            return DummyProject(path)

    assert reticulated.cli.Main(default_repo).projects == [
        DummyProject(default_repo / "project1"),
        DummyProject(default_repo / "subdir" / "project2"),
    ]


def test_projects__filtered_one_plugin(tmp_hookimpl, default_repo):
    @tmp_hookimpl
    def reticulated_get_project(path):
        if (path / "python.project").is_file():
            return DummyProject(path)

    @tmp_hookimpl
    def reticulated_ignore_project(project):
        return (project.root / "IGNOREME").exists()

    assert reticulated.cli.Main(default_repo).projects == [DummyProject(default_repo / "project1")]


def test_projects__filtered_multiple_plugins(tmp_hookimpl, default_repo):
    @tmp_hookimpl
    def reticulated_get_project(path):
        if (path / "python.project").is_file():
            return DummyProject(path)

    @tmp_hookimpl("plugin1")
    def reticulated_ignore_project(project):
        return (project.root / "IGNOREME").exists()

    @tmp_hookimpl("plugin2")  # noqa: F811
    def reticulated_ignore_project(project):
        return project.root.stem == "project1"

    assert reticulated.cli.Main(default_repo).projects == []
