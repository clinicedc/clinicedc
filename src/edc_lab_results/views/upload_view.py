from __future__ import annotations

import uuid
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ..forms import UploadResultFileForm
from ..models import UploadedResultFile


def _get_pending_dir() -> Path:
    base = Path(settings.EDC_LAB_RESULTS_UPLOAD_DIR).expanduser()
    return base / "pending"


class UploadView(EdcViewMixin, NavbarViewMixin, TemplateView):
    template_name = "edc_lab_results/upload.html"
    navbar_selected_item = "edc_lab_results"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        form = UploadResultFileForm() if "form" not in kwargs else kwargs["form"]
        recent_uploads = UploadedResultFile.objects.all()[:50]
        context.update(form=form, recent_uploads=recent_uploads)
        return context

    def post(self, request: object, *args: object, **kwargs: object) -> object:  # noqa: ARG002
        form = UploadResultFileForm(request.POST, request.FILES)
        if form.is_valid():
            files = form.cleaned_data["files"]
            pending_dir = _get_pending_dir()
            saved_count = 0
            for f in files:
                stored_name = f"{uuid.uuid4().hex}.pdf"
                dest = pending_dir / stored_name
                with dest.open("wb") as out:
                    out.writelines(f.chunks())
                UploadedResultFile.objects.create(
                    original_filename=f.name,
                    stored_filename=stored_name,
                    uploaded_by=request.user,
                )
                saved_count += 1
            if saved_count:
                messages.success(
                    request,
                    f"Uploaded {saved_count} file(s). Pending import.",
                )
            return HttpResponseRedirect(reverse("edc_lab_results:upload"))
        return self.render_to_response(self.get_context_data(form=form))
