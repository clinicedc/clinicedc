import urllib


class QueryStringViewMixin:

    @property
    def querystring(self):
        querystring = {}
        f = self.request.GET.get('f')
        e = self.request.GET.get('e')
        q = self.request.GET.get('q')
        o = self.request.GET.get('o')
        if f:
            querystring.update(f=f)
        if e:
            querystring.update(e=e)
        if q:
            querystring.update(q=q)
        if o:
            querystring.update(o=o)
        if querystring:
            return '?' + urllib.parse.urlencode(querystring)
        return ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            f=self.request.GET.get('f'),
            e=self.request.GET.get('e'),
            o=self.request.GET.get('o'),
            q=self.request.GET.get('q'),
            querystring=self.querystring)
        return context
