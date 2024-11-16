from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from celery import current_app, shared_task

from ..utils import process_repack_request as process_repack_request_util

if TYPE_CHECKING:

    from ..models import RepackRequest


@shared_task
def process_repack_request(repack_request: RepackRequest):
    process_repack_request_util(repack_request_id=repack_request.id)
    return None


@shared_task
def process_repack_request_queryset(repack_request_pks: list[UUID]):
    i = current_app.control.inspect()
    active_workers = i.active()
    if not active_workers:
        repack_request_pks = repack_request_pks[:1]
    for pk in repack_request_pks:
        process_repack_request_util(repack_request_id=pk)
    return None
