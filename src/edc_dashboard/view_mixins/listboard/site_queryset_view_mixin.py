from django.conf import settings


class SiteQuerysetViewMixin:

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        try:
            REVIEWER_SITE_ID = settings.REVIEWER_SITE_ID
        except AttributeError:
            REVIEWER_SITE_ID = 0
        if int(request.site.id) == int(REVIEWER_SITE_ID):
            try:
                options.pop('site')
            except KeyError:
                pass
        else:
            options.update(site=request.site)
        return options
