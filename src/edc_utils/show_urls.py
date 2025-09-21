# taken from django-extensions management command
# https://github.com/django-extensions/django-extensions/blob/master/django_extensions/management/commands/show_urls.py

from django.core.exceptions import ViewDoesNotExist
from django.urls import URLPattern, URLResolver, get_resolver


class RegexURLPattern:
    pass


class RegexURLResolver:
    pass


class LocaleRegexURLResolver:
    pass


def describe_pattern(p):
    return str(p.pattern)


def show_namespaces():
    """Returns a list of all registered URL namespaces."""
    resolver = get_resolver()
    return list(resolver.namespace_dict.keys())


def show_urls():
    """Return a list of all URL patterns in the project."""
    urls = []
    resolver = get_resolver()
    url_patterns = resolver.url_patterns
    for pattern in url_patterns:
        try:
            urls.append(f"URL: {pattern.pattern} -> View: {pattern.callback.__name__}")
        except AttributeError:
            urls.append(f"URL: {pattern.pattern}")
    return urls


def show_urls_from_patterns(urlpatterns, base="", namespace=None, search=None):
    urls = extract_views_from_urlpatterns(urlpatterns, base=base, namespace=namespace)
    if search:
        return [url[1] for url in urls if search in url[1]]
    return [url[1] for url in urls]


def show_url_names(urlpatterns, base="", namespace=None, search=None):
    """Returns a list of url names.

    For example:
        resolver = get_resolver()
        url_patterns = resolver.url_patterns
        pprint(show_url_names(url_patterns))
    """

    urls = extract_views_from_urlpatterns(urlpatterns, base=base, namespace=namespace)
    if search:
        return [url[2] for url in urls if search in url[2]]
    return [url[2] for url in urls]


def extract_views_from_urlpatterns(urlpatterns, base="", namespace=None):  # noqa
    """
    Return a list of views from a list of urlpatterns.
    Each object in the returned list is a three-tuple: (view_func, regex, name)
    """
    views = []
    for p in urlpatterns:
        if isinstance(p, (URLPattern, RegexURLPattern)):
            try:
                if not p.name:
                    name = p.name
                elif namespace:
                    name = f"{namespace}:{p.name}"
                else:
                    name = p.name
                pattern = describe_pattern(p)
                views.append((p.callback, base + pattern, name))
            except ViewDoesNotExist:
                continue
        elif isinstance(p, (URLResolver, RegexURLResolver)):
            try:
                patterns = p.url_patterns
            except ImportError:
                continue
            if namespace and p.namespace:
                _namespace = f"{namespace}:{p.namespace}"
            else:
                _namespace = p.namespace or namespace
            pattern = describe_pattern(p)
            views.extend(
                extract_views_from_urlpatterns(patterns, base + pattern, namespace=_namespace)
            )
        elif hasattr(p, "_get_callback"):
            try:
                views.append((p._get_callback(), base + describe_pattern(p), p.name))
            except ViewDoesNotExist:
                continue
        elif hasattr(p, "url_patterns") or hasattr(p, "_get_url_patterns"):
            try:
                patterns = p.url_patterns
            except ImportError:
                continue
            views.extend(
                extract_views_from_urlpatterns(
                    patterns, base + describe_pattern(p), namespace=namespace
                )
            )
        else:
            raise TypeError("%s does not appear to be a urlpattern object" % p)
    return views
