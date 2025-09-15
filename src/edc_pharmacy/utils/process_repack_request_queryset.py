from __future__ import annotations

from uuid import UUID

from celery import shared_task

from edc_utils.celery import celery_is_active, run_task_sync_or_async

from ..utils import process_repack_request


@shared_task
def process_repack_request_queryset(
    repack_request_pks: list[UUID], username: str = None
) -> None:
    if not celery_is_active():
        repack_request_pks = repack_request_pks[:1]
    for pk in repack_request_pks:
        run_task_sync_or_async(process_repack_request, repack_request_id=pk, username=username)


__all__ = ["process_repack_request_queryset"]
