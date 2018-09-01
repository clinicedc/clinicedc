from django import template
from django.conf import settings
from django.urls.base import reverse
from urllib.parse import urljoin, parse_qsl, urlencode, unquote


register = template.Library()


class Number:
    def __init__(self, number=None, url=None, current=None):
        self.number = number
        self.url = url
        self.active = 'active' if current else ''

    def __str__(self):
        return self.number

    def __repr__(self):
        return f'{self.__class__.__name__}<number={self.number} {self.active}>'


class UrlMaker:
    def __init__(self, base=None, querystring=None):
        self.base = base
        self.querystring = querystring

    def url(self, page):
        url = urljoin(self.base, str(page)) + '/'
        if self.querystring:
            return '?'.join([url, self.querystring])
        return url


def page_numbers(page, numpages, display=None):
    """Returns a list of x integers (display) relative to the value of n
    where n > 0 and the length of the list cannot exceed count.
    """
    page_numbers = None
    if page and numpages:
        min_n = page - 5
        min_n = 1 if min_n <= 0 else min_n
        max_n = min_n + 9
        max_n = numpages if max_n >= numpages else max_n
        page_numbers = [x for x in range(min_n, max_n + 1)]
    return page_numbers or []


@register.inclusion_tag(f'edc_dashboard/bootstrap{settings.EDC_BOOTSTRAP}/'
                        'paginator/paginator_row.html', takes_context=True)
def paginator_row(context):

    numbers = []
    first_url = None
    previous_url = None
    next_url = None
    last_url = None
    sub_text = None

    paginator_url = context.get('paginator_url')
    paginator = context.get('paginator')
    page_obj = context.get('page_obj')
    querystring = context.get('querystring')

    search_term = context.get('search_term')

    show = page_obj.has_other_pages()
    paginator_url = reverse(
        paginator_url, kwargs=context.get('paginator_url_kwargs'))
    if querystring:
        if '?' in querystring:
            querystring = querystring.split('?')[1]
        query_dict = parse_qsl(querystring)
        querystring = unquote(urlencode(query_dict))
    if show:
        url_maker = UrlMaker(base=paginator_url, querystring=querystring)
        if page_obj.has_previous():
            first_url = url_maker.url(1)
            previous_url = url_maker.url(page_obj.previous_page_number())
        if page_obj.has_next():
            next_url = url_maker.url(page_obj.next_page_number())
            last_url = url_maker.url(paginator.num_pages)

        for page in page_numbers(page_obj.number, paginator.num_pages):
            current = page_obj.number == page
            url = '#'
            if not current:
                url = url_maker.url(page)
            numbers.append(
                Number(number=page, url=url, current=current))
        sub_text = (
            f'Showing items {page_obj.start_index()} to {page_obj.end_index()} '
            f'of {paginator.count}.')

    return dict(
        page_obj=page_obj,
        show=show,
        first_url=first_url,
        previous_url=previous_url,
        next_url=next_url,
        last_url=last_url,
        numbers=numbers,
        search_term=search_term,
        sub_text=sub_text)
