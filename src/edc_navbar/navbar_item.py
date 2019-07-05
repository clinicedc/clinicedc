import copy

from django.apps import apps as django_apps
from django.conf import settings
from django.template.loader import render_to_string
from django.urls.base import reverse
from edc_dashboard.url_names import url_names, InvalidUrlName
from django.urls.exceptions import NoReverseMatch


class NavbarItemError(Exception):
    pass


class PermissionsCodenameError(Exception):
    pass


class NavbarItem:

    """A class that represents a single item on a navbar.
    """

    template_name = f"edc_navbar/bootstrap{settings.EDC_BOOTSTRAP}/navbar_item.html"

    def __init__(
        self,
        name=None,
        title=None,
        label=None,
        alt=None,
        url_name=None,
        html_id=None,
        glyphicon=None,
        fa_icon=None,
        icon=None,
        icon_width=None,
        icon_height=None,
        no_url_namespace=None,
        active=None,
        codename=None,
    ):
        self._reversed_url = None
        self.active = active
        self.alt = alt or label or name
        if fa_icon and fa_icon.startswith("fa-"):
            self.fa_icon = f"fa {fa_icon}"
        else:
            self.fa_icon = fa_icon
        self.glyphicon = glyphicon
        self.html_id = html_id or name
        self.icon = icon
        self.icon_height = icon_height
        self.icon_width = icon_width
        try:
            self.label = label
        except AttributeError:
            self.label = None
        self.name = name
        self.title = title or self.label or name.title()  # the anchor title

        try:
            self.url_name = url_names.get(url_name)
        except InvalidUrlName:
            self.url_name = url_name.split(":")[1] if no_url_namespace else url_name

        if not self.url_name:
            raise NavbarItemError(f"'url_name' not specified. See {repr(self)}")

        if self.url_name == "#":
            self.reversed_url = "#"
        else:
            try:
                self.reversed_url = reverse(self.url_name)
            except NoReverseMatch as e:
                raise NoReverseMatch(f"{e}. See {repr(self)}.")

        app_label, _codename = self.verify_codename(codename)
        self.codename = f"{app_label}.{_codename}"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(name={self.name}, "
            f"title={self.title}<url_name={self.url_name}>)"
        )

    def __str__(self):
        return f"{self.name}<url={self.url_name}>"

    def get_context(self, selected_item=None, **kwargs):
        """Returns a dictionary of context data.
        """
        context = copy.copy(self.__dict__)
        context.update(**kwargs)
        if selected_item == self.name or self.active:
            context.update(active=True)
        return context

    def render(self, request=None, **kwargs):
        """Render to string the template and context data.

        If permission codename is specified, check the user
        has permissions. If not return a disabled control.
        """
        context = self.get_context(**kwargs)
        if not self.codename:
            context.update(has_navbar_item_permission=True)
        else:
            context.update(
                has_navbar_item_permission=request.user.has_perm(self.codename)
            )
        return render_to_string(template_name=self.template_name, context=context)

    def verify_codename(self, dotted_codename=None):
        if not dotted_codename:
            raise PermissionsCodenameError(
                f"Invalid codename. May not be None. See {repr(self)}"
            )
        try:
            app_label, codename = dotted_codename.split(".")
        except ValueError:
            raise PermissionsCodenameError(
                f"Invalid codename. Got '{dotted_codename}'. See {repr(self)}."
            )
        if app_label not in [a.name for a in django_apps.get_app_configs()]:
            raise PermissionsCodenameError(
                f"Invalid app_label in codename. Expected format "
                f"'<app_label>.<some_codename>'. Got {dotted_codename}. "
                f"See {repr(self)}"
            )
        return app_label, codename
