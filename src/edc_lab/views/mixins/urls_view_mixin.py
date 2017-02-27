from django.apps import apps as django_apps


app_name = 'edc_lab'
app_config = django_apps.get_app_config(app_name)


class UrlsViewMixin:

    aliquot_listboard_url_name = app_config.aliquot_listboard_url_name
    manage_box_listboard_url_name = app_config.manage_box_listboard_url_name
    manifest_listboard_url_name = app_config.manifest_listboard_url_name
    manage_manifest_listboard_url_name = app_config.manage_manifest_listboard_url_name
    pack_listboard_url_name = app_config.pack_listboard_url_name
    process_listboard_url_name = app_config.process_listboard_url_name
    receive_listboard_url_name = app_config.receive_listboard_url_name
    requisition_listboard_url_name = app_config.requisition_listboard_url_name
    verify_box_listboard_url_name = app_config.verify_box_listboard_url_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            aliquot_listboard_url_name=self.aliquot_listboard_url_name,
            manage_box_listboard_url_name=self.manage_box_listboard_url_name,
            manifest_listboard_url_name=self.manifest_listboard_url_name,
            manage_manifest_listboard_url_name=self.manage_manifest_listboard_url_name,
            pack_listboard_url_name=self.pack_listboard_url_name,
            process_listboard_url_name=self.process_listboard_url_name,
            receive_listboard_url_name=self.receive_listboard_url_name,
            requisition_listboard_url_name=self.requisition_listboard_url_name,
            verify_box_listboard_url_name=self.verify_box_listboard_url_name,
        )
        return context
