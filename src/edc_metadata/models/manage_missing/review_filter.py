from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

from edc_model.models import BaseUuidModel


class ReviewFilter(BaseUuidModel):
    """A named, saved snapshot of the review board Filters panel.

    Stores the board's urlencoded filter querystring so it can be replayed by
    navigating to ``manage_missing_url?<query>``. Personal by default; ``shared``
    makes it visible to the whole team.
    """

    name = models.CharField(max_length=100)

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="+")

    query = models.TextField(
        default="", blank=True, help_text="urlencoded review board filter querystring"
    )

    shared = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Review filter"
        verbose_name_plural = "Review filters"
        ordering = ("name",)
        constraints = (
            UniqueConstraint(
                fields=["user", "name"],
                name="%(app_label)s_%(class)s_user_name_uniq",
            ),
        )
