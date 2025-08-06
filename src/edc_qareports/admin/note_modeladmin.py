from django.contrib import admin

from ..admin_site import edc_qareports_admin
from ..forms import NoteForm
from ..modeladmin_mixins import NoteModelAdminMixin
from ..models import Note


@admin.register(Note, site=edc_qareports_admin)
class NoteModelAdmin(
    NoteModelAdminMixin,
    admin.ModelAdmin,
):
    """A modeladmin class for the Note model."""

    form = NoteForm
    note_template_name = "edc_qareports/qa_report_note.html"
