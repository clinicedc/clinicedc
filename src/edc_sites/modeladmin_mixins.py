class SiteModelAdminMixin:
    """Adds the current site to the form from the request object.

    Use together with the `SiteModelFormMixin`.
    """

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.currrent_site = request.site
        return form
