from celery import current_app
from celery.result import AsyncResult
from django.conf import settings
from kombu.exceptions import OperationalError

celery_enabled = getattr(settings, "CELERY_ENABLED", False)


def run_task_sync_or_async(task, *args, **kwargs) -> AsyncResult:
    """Run a task with celery if running"""

    if not celery_enabled or not celery_is_active() or current_app.conf.task_always_eager:
        return task(*args, **kwargs)
    return task.delay(*args, **kwargs)


def celery_is_active() -> dict:
    """Inspect if workers are running, e.g was celery
    service started.
    """
    i = current_app.control.inspect()
    try:
        return i.active()
    except OperationalError:
        return {}


def get_task_result(obj) -> AsyncResult | None:
    """Query celery task and return result or None

    If celery not running will raise an exception
    that is caught here.
    """
    result = None
    if obj.task_id:
        try:
            result = AsyncResult(str(obj.task_id))
        except (TypeError, ValueError):
            pass
    return result


__all__ = ["celery_is_active", "get_task_result", "run_task_sync_or_async"]
