from .utils import raise_on_save_if_reviewer


class ModelAdminSiteMixin:
    def save_model(self, request, *args):
        raise_on_save_if_reviewer(site_id=request.site.id)
        super().save_model(request, *args)
