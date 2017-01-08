

class Base:

    dashboard_url = 'dashboard_url'
    base_html = 'edc_base/base.html'

    def pk_wrapper(self, obj):
        obj.str_pk = str(obj.id)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            base_html=self.base_html,
            dasbboard_url=self.dashboard_url)
        return context
