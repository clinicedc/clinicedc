from celery import current_app
from celery.result import AsyncResult


def run_task_sync_or_async(task, *args, **kwargs):
    i = current_app.control.inspect()
    active_workers = i.active()

    if current_app.conf.task_always_eager or not active_workers:
        return task(*args, **kwargs)
    else:
        return task.delay(*args, **kwargs)


def celery_is_active():
    i = current_app.control.inspect()
    return i.active()


def get_task_result(obj) -> AsyncResult | None:
    result = None
    if obj.task_id:
        try:
            result = AsyncResult(str(obj.task_id))
        except (TypeError, ValueError):
            pass
    return result


__all__ = ["run_task_sync_or_async", "get_task_result", "celery_is_active"]
