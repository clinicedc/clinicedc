from __future__ import annotations

from django.db import models

from edc_model.models import BaseUuidModel

from ..utils import PrivateStorage, destination_subfolder_name


def upload_to(instance: SourceDocument, filename: str) -> str:
    # content-addressed: dedupe is free and names never collide
    return f"{destination_subfolder_name}/{instance.sha256[:2]}/{instance.sha256}.pdf"


class SourceDocument(BaseUuidModel):
    sha256 = models.CharField(max_length=64, unique=True, db_index=True)

    pdf = models.FileField(upload_to=upload_to, storage=PrivateStorage, max_length=200)

    filename = models.CharField(max_length=200, db_index=True)

    laboratory = models.CharField(max_length=25, blank=True, default="")

    file_size = models.IntegerField(null=True)

    def __str__(self):
        return self.filename

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Source document"
        verbose_name_plural = "Source documents"
