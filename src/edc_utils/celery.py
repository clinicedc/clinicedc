from celery import current_app
from celery.result import AsyncResult


def run_task_sync_or_async(task, *args, **kwargs):
    """Run a task with celery if running"""
    if current_app.conf.task_always_eager or not celery_is_active():
        return task(*args, **kwargs)
    else:
        return task.delay(*args, **kwargs)


def celery_is_active() -> dict:
    """Inspect if workers are running, e.g was celery
    service started.
    """
    i = current_app.control.inspect()
    return i.active()


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


__all__ = ["run_task_sync_or_async", "get_task_result", "celery_is_active"]
