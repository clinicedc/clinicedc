from django.conf import settings
from django.contrib.sites.models import Site
from django.db import connection, models
from django.db.models import DO_NOTHING, Index
from edc_utils import get_utcnow

from .qa_reports_permissions import qa_reports_permissions


class QaReportModelMixin(models.Model):

    report_model = models.CharField(max_length=50)

    subject_identifier = models.CharField(max_length=25)

    site = models.ForeignKey(Site, on_delete=DO_NOTHING)

    created = models.DateTimeField(default=get_utcnow)

    @classmethod
    def refresh_db_view(cls):
        """Manually refresh the database view for models declared
        with `django_db_views.DBView`.

        Mostly useful when Django raises an OperationalError with a
        restored DB complaining of 'The user specified as a definer
        (user@server) does not exist'.

        This does not replace generating a migration with `viewmigration`
        and running the migration.
        """
        try:
            sql = cls.view_definition.get(settings.DATABASES["default"]["ENGINE"])  # noqa
        except AttributeError as e:
            raise AttributeError(
                f"Is this model linked to a view? Declare model with `DBView`. Got {e}"
            )
        else:
            sql = sql.replace(";", "")
            cursor = connection.cursor()
            cursor.execute(
                f"drop view {cls._meta.db_table};create view {cls._meta.db_table} as {sql};"
            )

    class Meta:
        abstract = True
        default_permissions = qa_reports_permissions
        indexes = [Index(fields=["subject_identifier", "site"])]
