from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import View

from ..models import UploadedResultFile
from ..models.uploaded_result_file import PENDING


class DeleteUploadView(View):
    """Delete a pending uploaded file from disk and database."""

    def post(self, request: object, pk: str) -> HttpResponseRedirect:
        try:
            upload = UploadedResultFile.objects.get(pk=pk, status=PENDING)
        except UploadedResultFile.DoesNotExist as e:
            raise Http404("Upload not found or not pending.") from e

        # Remove file from disk
        base = Path(settings.EDC_LAB_RESULTS_UPLOAD_DIR).expanduser()
        file_path = base / "pending" / upload.stored_filename
        if file_path.exists():
            file_path.unlink()

        original_name = upload.original_filename
        upload.delete()

        messages.success(request, f"Removed: {original_name}")
        return HttpResponseRedirect(reverse("edc_lab_results:upload"))
