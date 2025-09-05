edc-qareports
=============

This module helps you represent SQL VIEWS as QA Reports using Django Admin.

In clinicedc/edc projects, QA reports are in the ``<my_app>_reports`` module.

Installation
------------

Add to settings.INSTALLED_APPS:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        "edc_qareports.apps.AppConfig",
        ...
        ]

Add to project URLS:

.. code-block:: python

    # urls.py
    urlpatterns = [
        ...
        *paths_for_urlpatterns("edc_qareports"),
        ...
        ]

Custom QA / data management reports using SQL VIEWS
---------------------------------------------------

Although not absolutely necessary, it is convenient to base a QA report on an SQL VIEW. As
data issues are resolved, the SQL VIEW reflects the current data.

A QA report based on an SQL VIEW can be represented by a model class. By registering the model class in Admin, all the functionality of the ModelAdmin class is available to show the report.

First, within your EDC project, create a `<myapp>_reports` app. For example `Meta Reports`.

.. code-block:: bash

    meta_edc
    meta_edc/meta_reports
    meta_edc/meta_reports/admin
    meta_edc/meta_reports/admin/dbviews
    meta_edc/meta_reports/admin/dbviews/my_view_in_sql_admin.py
    meta_edc/meta_reports/migrations
    meta_edc/meta_reports/migrations/0001_myviewinsql.py
    meta_edc/meta_reports/models
    meta_edc/meta_reports/models/dbviews
    meta_edc/meta_reports/models/dbviews/mymodel/unmanaged_model.py
    meta_edc/meta_reports/models/dbviews/mymodel/view_definition.py
    meta_edc/meta_reports/admin_site.py
    meta_edc/meta_reports/apps.py
    meta_edc/ ...

the ``apps.py`` might look like this:

.. code-block:: python

    from django.apps import AppConfig as DjangoAppConfig

    class AppConfig(DjangoAppConfig):
        name = "meta_reports"
        verbose_name = "META Reports"
        include_in_administration_section = True


QA Report as an SQL VIEW
++++++++++++++++++++++++
Now that you have created the basic structure for the Reports App, create an SQL VIEW. Some rules apply:

* To show the model class in Admin, the SQL VIEW needs at least an ID column.
* To use the EDC ModelAdmin classes, include ``id``, ``subject_identifier``, ``site_id``, ``created`` and ``report_model``.
* Columns ``id``, ``created`` and ``report_model`` are generated columns from the SQL VIEW, not values coming from the underlying SQL statement / data tables.
* Column ``report_model`` is in label_lower format.
* Suffix the view name with ``_view``.

To manage SQL view code, we use ``django_dbviews``. This module helps by using migrations to manage changes to the SQL view code.


The ``view_defintion.py`` might look like this:

.. code-block:: sql

    from edc_qareports.sql_generator import SqlViewGenerator

    def get_view_definition() -> dict:
        subquery = """
            select subject_identifier, site_id, appt_datetime, `first_value`,
            `second_value`, `third_value`,
            datediff(`third_date`, `first_date`) as `interval_days`,
            datediff(now(), `first_date`) as `from_now_days`
            from (
                select subject_identifier, site_id, appt_datetime,
                FIRST_VALUE(visit_code) OVER w as `first_value`,
                NTH_VALUE(visit_code, 2) OVER w as `second_value`,
                NTH_VALUE(visit_code, 3) OVER w as `third_value`,
                FIRST_VALUE(appt_datetime) OVER w as `first_date`,
                NTH_VALUE(appt_datetime, 3) OVER w as `third_date`
                from edc_appointment_appointment where visit_code_sequence=0 and appt_status="New"
                and appt_datetime <= now()
                WINDOW w as (PARTITION BY subject_identifier order by appt_datetime ROWS UNBOUNDED PRECEDING)
            ) as B
            where `second_value` is not null and `third_value` is not null
            """  # noqa
        sql_view = SqlViewGenerator(
            report_model="meta_reports.unattendedthreeinrow",
            ordering=["subject_identifier", "site_id"],
        )
        return {
            "django.db.backends.mysql": sql_view.as_mysql(subquery),
            "django.db.backends.postgresql": sql_view.as_postgres(subquery),
            "django.db.backends.sqlite3": sql_view.as_sqlite(subquery),
        }

Using a model class to represent your QA Report
+++++++++++++++++++++++++++++++++++++++++++++++

An SQL VIEW is not a table so configure an unmanaged model class by setting ``managed=False``. ``makemigrations`` creates migrations for unmanaged models but never calls ``CreateModel``.

The unmanaged model class would be something like this:

.. code-block:: python

    class MyViewInSql(QaReportModelMixin, models.Model):

        col1 = models.CharField(max_length=25)

        col2 = models.IntegerField()

        col3 = models.DateTimeField()

        class Meta:
            managed = False
            db_table = "my_view_in_sql_view"
            verbose_name = "blah blah"
            verbose_name_plural = "blah blah"

You can store the SQL statement anywhere but we put it in the same folder as
the model class using the same file name as the model class but with file extension ``.sql``

Using a migration to read the SQL statement
+++++++++++++++++++++++++++++++++++++++++++

Create an empty migration in the reports app and read the SQL file in the migration

.. code-block:: python

    ...

    operations = [
        migrations.RunSQL(
            read_unmanaged_model_sql("my_view_in_sql.sql", app_name="meta_reports")
        ),
    ]


IMPORTANT: If you change the SQL VIEW, update the ``.sql`` file and create a new migration
that drops and re-creates the SQL VIEW.

.. code-block:: python

    ...

    operations = [
        migrations.RunSQL("drop view my_view_in_sql_view"),
        migrations.RunSQL(
            read_unmanaged_model_sql("my_view_in_sql.sql", app_name="meta_reports")
        ),
    ]


Linking ``QaReportNote`` with your QA Report
++++++++++++++++++++++++++++++++++++++++++++

You can link your QA Report in Admin to model ``QaReportNote``. The ``QaReportNote``
model class is used to track the ``status`` of the report item and provide a space for any
notes.

To use ``QaReportNote`` with your QA report, declare the QA Report admin class with ``QaReportWithNoteModelAdminMixin``.

.. code-block:: python

    from django.contrib import admin
    from edc_model_admin.dashboard import ModelAdminDashboardMixin
    from edc_model_admin.mixins import TemplatesModelAdminMixin
    from edc_qareports.admin import QaReportWithNoteModelAdminMixin
    from edc_sites.admin import SiteModelAdminMixin
    from edc_visit_schedule.admin import ScheduleStatusListFilter

    from ...admin_site import meta_reports_admin
    from ...models import MyViewInSql


    @admin.register(MyViewInSql, site=meta_reports_admin)
    class MyViewInSqlAdmin(
        QaReportWithNoteModelAdminMixin,
        SiteModelAdminMixin,
        ModelAdminDashboardMixin,
        TemplatesModelAdminMixin,
        admin.ModelAdmin,
    ):
        ordering = ["site", "subject_identifier"]

        list_display = [
            "dashboard",
            "subject",
            "col1",
            "col2",
            "col3",
            "created",
        ]

        list_filter = [ScheduleStatusListFilter, "col1", "col3"]

        search_fields = ["id", "subject_identifier"]

        @admin.display(description="Subject", ordering="subject_identifier")
        def subject(self, obj):
            return obj.subject_identifier

Granting access to your QA Report
+++++++++++++++++++++++++++++++++

Add the QA report codenames to your local app, create a group and add the group to the QA_REPORTS_ROLE.

In this example the app is called ``meta_reports`` and the group is ``META_REPORTS``.

(Note: If your app has an ``auth`` module (e.g. ``meta_auth``) put these lines there.)

.. code-block:: python

    # meta_reports/auth_objects.py

    reports_codenames = [c for c in get_app_codenames("meta_reports")]

.. code-block:: python

    # meta_reports/auths.py

    site_auths.add_group(*reports_codenames, name=META_REPORTS)
    # add the group to the QA_REPORTS role
    site_auths.update_role(META_REPORTS, name=QA_REPORTS_ROLE)

