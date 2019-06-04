from edc_constants.constants import OPEN, FEEDBACK, CLOSED
from django.db import models
from django.db.models.deletion import PROTECT
from edc_model.models import BaseUuidModel


from .data_manager_query import DataManagerQuery
from .data_dictionary import DataDictionary
from .visit_schedule import VisitSchedule


STATUS = ((OPEN, "Open"), (FEEDBACK, "Feedback"), (CLOSED, "Closed"))


class Query(BaseUuidModel):

    data_manager_query = models.ForeignKey(DataManagerQuery, on_delete=PROTECT)

    title = models.CharField(
        max_length=35, help_text="Provide a short description of this query"
    )

    visit_schedule = models.ManyToManyField(
        VisitSchedule, verbose_name="Visit(s)", help_text="select all that apply"
    )

    data_dictionary = models.ManyToManyField(
        DataDictionary, verbose_name="Question(s)", help_text="select all that apply"
    )

    query = models.TextField(help_text="Describe the query in detail.")

    comment = models.TextField(
        null=True,
        blank=True,
        help_text="Any comment or question from the site or clinic concerning this query ",
    )

    status = models.CharField(
        max_length=25,
        choices=STATUS,
        default=OPEN,
        help_text="Change to CLOSED when all issues related to this query are resolved.",
    )

    field_name = models.CharField(max_length=50, editable=False)

    def __str__(self):
        return f"{self.title} {self.data_manager_query.identifier}"
