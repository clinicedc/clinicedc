from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_base import convert_php_dateformat
from urllib.parse import urlparse, parse_qsl

from .site_action_items import site_action_items


class ActionItemHelper:

    def __init__(self, model_wrapper=None, action_item=None, href=None):
        self._parent_reference_obj = None
        self._parent_reference_url = None
        self._reference_obj = None
        self._reference_url = None
        self._related_reference_obj = None
        self._related_reference_url = None
        if model_wrapper:
            self.action_item = model_wrapper.object
            self.href = model_wrapper.href
        else:
            self.action_item = action_item
            self.href = href
        self.action_identifier = self.action_item.action_identifier
        self.action_cls = site_action_items.get(
            self.action_item.reference_model_cls.action_name)
        if self.action_item.last_updated:
            # could also use action_item.linked_to_reference?
            date_format = convert_php_dateformat(settings.SHORT_DATE_FORMAT)
            last_updated = self.action_item.last_updated.strftime(date_format)
            user_last_updated = self.action_item.user_last_updated
            self.last_updated_text = (
                f'Last updated on {last_updated} by {user_last_updated}.')
        else:
            self.last_updated_text = 'This action item has not been updated.'

    @property
    def reference_obj(self):
        """Returns the reference model instance or None.
        """
        if not self._reference_obj:
            try:
                self._reference_obj = self.action_item.reference_obj
            except ObjectDoesNotExist:
                pass
        return self._reference_obj

    @property
    def reference_url(self):
        """Returns the add/change url for the reference model instance.
        """
        if not self._reference_url:
            opts = dict(
                action_item=self.action_item,
                action_identifier=self.action_identifier,
                reference_obj=self.reference_obj,
                **self.get_query_dict())
            self._reference_url = self.action_cls.reference_url(**opts)
        return self._reference_url

    @property
    def parent_reference_obj(self):
        """Returns the parent reference model instance or None.
        """
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
                query_dict = self.get_query_dict()
                try:
                    subject_visit = self.parent_reference_obj.visit
                except AttributeError:
                    pass
                else:
                    # parent reference model is a CRF, add visit to querystring
                    query_dict.update({
                        self.parent_reference_obj.visit_model_attr(): str(subject_visit.pk),
                        'appointment': str(subject_visit.appointment.pk)})
                self._parent_reference_url = (
                    self.action_cls.reference_url(
                        reference_obj=self.parent_reference_obj,
                        action_item=self.action_item,
                        action_identifier=self.action_identifier,
                        **query_dict))
        return self._parent_reference_url

    @property
    def related_reference_obj(self):
        """Returns the change url for the related reference
        model instance or None.
        """
        if not self._related_reference_obj:
            try:
                self._related_reference_obj = self.action_item.related_reference_obj
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
                query_dict = self.get_query_dict()
                try:
                    subject_visit = self.related_reference_obj.visit
                except AttributeError:
                    pass
                else:
                    # related reference model is a CRF
                    query_dict.update({
                        self.related_reference_obj.visit_model_attr(): str(subject_visit.pk),
                        'appointment': str(subject_visit.appointment.pk)})
                self._related_reference_url = (
                    self.action_cls.reference_url(
                        reference_obj=self.related_reference_obj,
                        action_item=self.action_item,
                        action_identifier=self.action_identifier,
                        **query_dict))
        return self._related_reference_url

    @property
    def action_item_reason(self):
        try:
            action_item_reason = self.parent_reference_obj.action_item_reason
        except AttributeError:
            try:
                action_item_reason = self.related_reference_obj.action_item_reason
            except AttributeError:
                action_item_reason = None
        return action_item_reason

    @property
    def reference_model_name(self):
        try:
            reference_model_name = (
                f'{self.action_item.reference_model_cls._meta.verbose_name} '
                f'{str(self.reference_obj or "")}')
        except AttributeError:
            reference_model_name = None
        return reference_model_name

    @property
    def parent_reference_model_name(self):
        try:
            parent_reference_model_name = (
                f'{self.action_item.parent_reference_model_cls._meta.verbose_name} '
                f'{str(self.parent_reference_obj)}')
        except AttributeError:
            parent_reference_model_name = None
        return parent_reference_model_name

    @property
    def related_reference_model_name(self):
        try:
            related_reference_model_name = (
                f'{self.action_item.related_reference_model_cls._meta.verbose_name} '
                f'{str(self.related_reference_obj)}')
        except AttributeError:
            related_reference_model_name = None
        return related_reference_model_name

    def get_context(self):
        """Returns a dictionary of instance attr.
        """
        return dict(
            action_identifier=self.action_identifier,
            action_instructions=self.action_item.instructions,
            action_item_color=self.action_cls.color_style,
            action_item_reason=self.action_item_reason,
            display_name=self.action_item.action_type.display_name,
            href=self.href,
            last_updated_text=self.last_updated_text,
            name=self.action_item.action_type.name,
            parent_action_item=self.action_item.parent_action_item,
            parent_reference_obj=self.parent_reference_obj,
            parent_reference_identifier=self.action_item.parent_reference_identifier,
            parent_reference_model_name=self.parent_reference_model_name,
            parent_reference_url=self.parent_reference_url,
            priority=self.action_item.priority or '',
            reference_model_name=self.reference_model_name,
            reference_obj=self.reference_obj,
            reference_url=self.reference_url,
            related_reference_identifier=self.action_item.related_reference_identifier,
            related_reference_obj=self.related_reference_obj,
            related_reference_model_name=self.related_reference_model_name,
            related_reference_url=self.related_reference_url,
            report_datetime=self.action_item.report_datetime,
            status=self.action_item.get_status_display(),
        )
