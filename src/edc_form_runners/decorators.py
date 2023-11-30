from .exceptions import FormRunnerRegisterError
from .form_runner import FormRunner
from .site import site_form_runners


def register(**kwargs):
    """Registers a custom form runner."""

    def _wrapper(form_runner_cls):
        if not issubclass(form_runner_cls, (FormRunner,)):
            raise FormRunnerRegisterError(
                f"Wrapped class must a FormRunner class. Got {form_runner_cls}."
            )
        site_form_runners.register(runner=form_runner_cls)
        return form_runner_cls

    return _wrapper
