from edc_sites import get_site_name
from import_export import resources
from import_export.fields import Field


class CrfModelResource(resources.ModelResource):

    subject_identifier = Field(column_name="subject_identifier")

    visit_code = Field(column_name="visit_code")

    visit_code_sequence = Field(column_name="visit_code_sequence")

    visit_datetime = Field(column_name="visit_datetime")

    site_name = Field(column_name="site_name")

    site_code = Field(column_name="site_code")

    def dehydrate_subject_identifier(self, obj):
        return obj.subject_visit.subject_identifier

    def dehydrate_visit_code(self, obj):
        return obj.subject_visit.visit_code

    def dehydrate_visit_code_sequence(self, obj):
        return obj.subject_visit.visit_code_sequence

    def dehydrate_visit_datetime(self, obj):
        return obj.subject_visit.report_datetime

    def dehydrate_site_name(self, obj):
        return get_site_name(obj.site.id)

    def dehydrate_site_code(self, obj):
        return obj.site.id

    class Meta:
        exclude = (
            "hostname_modified",
            "device_created",
            "device_modified",
            "site",
        )


class NonCrfModelResource(resources.ModelResource):

    site_name = Field(column_name="site_name")

    site_code = Field(column_name="site_code")

    def dehydrate_site_name(self, obj):
        return get_site_name(obj.site.id)

    def dehydrate_site_code(self, obj):
        return obj.site.id

    class Meta:
        exclude = (
            "hostname_modified",
            "device_created",
            "device_modified",
            "site",
        )
