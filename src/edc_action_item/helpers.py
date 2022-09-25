import logging
from urllib.parse import parse_qsl, unquote, urlencode, urlparse
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from edc_dashboard.utils import get_bootstrap_version
from edc_utils import convert_php_dateformat

from .site_action_items import site_action_items

logger = logging.getLogger(__name__)


class ActionItemHelperError(Exception):
    pass


class ActionItemHelper:

    action_item_reason_template_name = (
        f"edc_action_item/bootstrap{get_bootstrap_version()}/action_item_reason.html"
    )

    def __init__(
        self, action_item=None, href=None, action_name=None, related_action_item=None
    ):
        self._parent_reference_obj = None
        self._parent_reference_url = None
        self._reference_obj = None
        self._reference_url = None
        self._related_reference_obj = None
        self._related_reference_url = None
        self.href = href
        self.last_updated_text = "This action item has not been updated."
        if not action_item and action_name:
            self.action_identifier = None
            self.action_item = None
            self.action_cls = site_action_items.get(action_name)
            self.related_action_item = related_action_item
            if self.action_cls.related_reference_fk_attr and not related_action_item:
                raise ActionItemHelperError(
                    f"Expected related_action_item. Got None. "
                    f"Related field attribute is '"
                    f"{self.action_cls.related_reference_fk_attr}'. "
                    f"See {repr(self)}."
                )
        else:
            self.action_identifier = action_item.action_identifier
            self.action_item = action_item
            self.action_cls = action_item.reference_model_cls.get_action_cls()
            self.related_action_item = self.action_item.related_action_item
            if self.action_item.last_updated:
                # could also use action_item.linked_to_reference?
                date_format = convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                last_updated = self.action_item.last_updated.strftime(date_format)
                user_last_updated = self.action_item.user_last_updated
                self.last_updated_text = (
                    f"Last updated on {last_updated} by {user_last_updated}."
                )

    def __repr__(self):
        return f"{self.__class__.__name__}(action_name={self.action_cls})"

    def get_url(self, model_obj=None, model_cls=None, **kwargs):
        """Returns a relative add URL with querystring that can
        get back to the subject dashboard on save.

        Adds visit fk to the querystring if possible.
        """
        opts = dict(**self.get_query_dict(), **kwargs)
        if self.action_identifier:
            opts.update(action_identifier=self.action_identifier)

        if self.action_cls.related_reference_fk_attr:
            try:
                related_reference_obj = (
                    self.action_cls.related_reference_model_cls().objects.get(
                        action_item=self.related_action_item
                    )
                )
            except ObjectDoesNotExist as e:
                logger.warning(
                    f"{e} See {self.action_item}. Related action identifier"
                    f"='{self.action_item.related_action_identifier}'."
                )
                opts.update({self.action_cls.related_reference_fk_attr: None})
            else:
                opts.update(
                    {self.action_cls.related_reference_fk_attr: str(related_reference_obj.pk)}
                )
        if model_obj:
            try:
                model_obj.related_visit_model_attr()
            except AttributeError:
                pass
            else:
                visit_obj = getattr(model_obj, model_obj.related_visit_model_attr())
                opts.update(
                    {
                        model_obj.related_visit_model_attr(): str(visit_obj.pk),
                        "appointment": str(visit_obj.appointment.pk),
                    }
                )
            path = model_obj.get_absolute_url()
        else:
            path = model_cls().get_absolute_url()
        query = unquote(urlencode(opts))
        if query:
            return "?".join([path, query])
        return path

    @property
    def reference_obj(self):
        """Returns the reference model instance or None."""
        if not self._reference_obj:
            try:
                self._reference_obj = self.action_item.reference_obj
            except (AttributeError, ObjectDoesNotExist):
                pass
        return self._reference_obj

    @property
    def reference_url(self):
        """Returns the url for the reference object."""
        if not self._reference_url:
            self._reference_url = self.get_url(
                model_obj=self.reference_obj,
                model_cls=self.action_cls.reference_model_cls(),
            )
        return self._reference_url

    @property
    def parent_reference_obj(self):
        """Returns the parent reference model instance or None."""
        if not self._parent_reference_obj:
            try:
                self._parent_reference_obj = self.action_item.parent_reference_obj
            except (AttributeError, ObjectDoesNotExist):
                pass
        return self._parent_reference_obj

    def get_query_dict(self):
        return dict(parse_qsl(urlparse(self.href).query))

    @property
    def parent_reference_url(self):
        """Returns the change url for the parent reference
        model instance or None.
        """
        if not self._parent_reference_url:
            if self.parent_reference_obj:
                kwargs = dict(
                    model_obj=self.parent_reference_obj,
                    model_cls=self.parent_reference_obj.__class__,
                )
                self._parent_reference_url = self.get_url(**kwargs)
        return self._parent_reference_url

    @property
    def related_reference_obj(self):
        """Returns the change url for the related reference
        model instance or None.
        """
        if not self._related_reference_obj:
            try:
                self._related_reference_obj = self.related_action_item.reference_obj
            except (AttributeError, ObjectDoesNotExist):
                pass
        return self._related_reference_obj

    @property
    def related_reference_url(self):
        """Returns the change url for the related reference
        model instance or None.
        """
        if not self._related_reference_url:
            if self.related_reference_obj:
                kwargs = dict(
                    model_obj=self.related_reference_obj,
                    model_cls=self.related_reference_obj.__class__,
                )
                self._related_reference_url = self.get_url(**kwargs)
        return self._related_reference_url

    def render_action_item_reasons(self):
        action_item_reasons = []
        objects = [
            self.reference_obj,
            self.parent_reference_obj,
            self.related_reference_obj,
        ]
        for obj in objects:
            try:
                action_item_reasons.append(obj.get_action_item_reason())
            except AttributeError as e:
                if "get_action_item_reason" not in str(e):
                    raise
        action_item_reasons = list(set(action_item_reasons))
        return render_to_string(
            self.action_item_reason_template_name,
            context={"action_item_reasons": action_item_reasons},
        )

    @property
    def reference_model_name(self):
        try:
            reference_model_name = (
                f"{self.action_item.reference_model_cls._meta.verbose_name} "
                f'{str(self.reference_obj or "")}'
            )
        except AttributeError:
            reference_model_name = None
        return reference_model_name

    @property
    def parent_reference_model_name(self):
        try:
            parent_reference_model_name = (
                f"{self.action_item.parent_action_item.reference_model_cls._meta.verbose_name} "  # noqa
                f"{str(self.parent_reference_obj)}"
            )
        except AttributeError:
            parent_reference_model_name = None
        return parent_reference_model_name

    @property
    def related_reference_model_name(self):
        try:
            related_reference_model_name = (
                f"{self.related_action_item.reference_model_cls._meta.verbose_name} "
                f"{str(self.related_reference_obj)}"
            )
        except AttributeError:
            related_reference_model_name = None
        return related_reference_model_name

    def get_context(self):
        """Returns a dictionary of instance attr."""
        context = {}
        if self.action_item.parent_action_item:
            context.update(
                parent_action_identifier=self.action_item.parent_action_item.action_identifier
            )
        if self.related_action_item:
            context.update(
                related_action_identifier=self.related_action_item.action_identifier
            )
        context.update(
            action_identifier=self.action_identifier,
            action_instructions=self.action_item.instructions,
            action_item_color=self.action_item.action.get_color_style(),
            action_item_reason=self.render_action_item_reasons(),
            display_name=self.action_item.action.get_display_name(),
            href=self.href,
            last_updated_text=self.last_updated_text,
            name=self.action_item.action_type.name,
            parent_action_item=self.action_item.parent_action_item,
            parent_reference_obj=self.parent_reference_obj,
            parent_reference_model_name=self.parent_reference_model_name,
            parent_reference_url=self.parent_reference_url,
            popover_title=self.action_item.action.get_popover_title(),
            priority=self.action_item.action.get_priority(),
            reference_model_name=self.reference_model_name,
            reference_obj=self.reference_obj,
            reference_url=self.reference_url,
            related_reference_obj=self.related_reference_obj,
            related_reference_model_name=self.related_reference_model_name,
            related_reference_url=self.related_reference_url,
            report_datetime=self.action_item.report_datetime.astimezone(
                ZoneInfo(settings.TIME_ZONE)
            ),
            status=self.action_item.action.get_status(),
        )
        return context
