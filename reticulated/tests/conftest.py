import functools

import pluggy
import pytest

import reticulated


@pytest.fixture
def tmp_hookimpl(mocker):
    """A fixture which allows you to declare registered hookimpls scoped to the test.

    The fixture is intended to be used as a decorator and has 2 ways of calling it:
        - Without any arguments: This registers the hookimpl under a fake class named "DEFAULT"
        - With a string: This registers the hookimpl under a class with the given name

    The class names are useful for debugging and for testing multiple entrypoints defining the same
    hookimpl.

    #TODO: Example
    """

    hookimpl_classes = {"DEFAULT": type("DEFAULT", tuple(), {})}

    def _decorator_impl(func, class_name):
        hookimpl = reticulated.hookimpl(func)
        if class_name not in hookimpl_classes:
            hookimpl_classes[class_name] = type(class_name, tuple(), {})

        setattr(hookimpl_classes[class_name], func.__name__, hookimpl)
        return hookimpl

    def decorator(func_or_str):
        if isinstance(func_or_str, str):
            return functools.partial(_decorator_impl, class_name=func_or_str)
        return _decorator_impl(func_or_str, "DEFAULT")

    def also_register_temp_hookimpls(plugin_manager: pluggy.PluginManager, *args, **kwargs):
        """Registers the temporary hookimpls."""
        for cls in hookimpl_classes.values():
            plugin_manager.register(cls)

        return mocker.DEFAULT

    # Convenience place for us to inject some code to make it look like the temporary hook impls
    # are declared as part of setuptools entrypoints
    mocker.patch.object(
        pluggy.PluginManager,
        "load_setuptools_entrypoints",
        wraps=pluggy.PluginManager.load_setuptools_entrypoints,
        side_effect=also_register_temp_hookimpls,
        autospec=True,
    )

    return decorator
