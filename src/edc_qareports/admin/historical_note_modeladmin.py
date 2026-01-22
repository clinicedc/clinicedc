from django.contrib import admin
from edc_model.admin import HistoricalModelAdminMixin
from edc_model_admin.history import SimpleHistoryAdmin

from ..admin_site import edc_qareports_admin
from ..models import Note
from .model_admin_mixin import ModelAdminMixin


@admin.register(Note.history.model, site=edc_qareports_admin)
class HistoricalNoteModelAdmin(
    HistoricalModelAdminMixin,
    ModelAdminMixin,
    SimpleHistoryAdmin,
):
    """A modeladmin class for the Note model."""

    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20
    change_list_note_url_name = "edc_qareports_admin:edc_qareports_note_changelist"

    list_display = (
        "subject_identifier",
        "report_model",
        "status",
        "history_type",
        "formatted_history_date",
        "revision",
        "history_id",
    )

    search_fields = ("report_model", "subject_identifier")
