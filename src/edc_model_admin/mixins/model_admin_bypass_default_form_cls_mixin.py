from __future__ import annotations

from functools import partial

from django import forms
from django.contrib import messages
from django.contrib.admin.utils import flatten_fieldsets
from django.contrib.messages import MessageFailure
from django.core.exceptions import FieldError
from django.forms.models import modelform_defines_fields, modelform_factory
from django.utils.html import format_html
from edc_sites.modelform_mixins import SiteModelFormMixin


class ModelAdminBypassDefaultFormClsMixin:

    """A modeladmin mixin to set the admin class's modelform conditionally
    based on a special data manager permission codename.

    Position this mixin just before `admin.ModelAdmin` to ensure the
    correct MRO for `get_form`.

    The custom modelform factory returns a basic modelform for the
    given admin model WITHOUT ANY validation checks.

    This special case can be used briefly, carefully and by an
    experienced user to update a form that cannot be updated
    because of a blocking validation check. The user MUST know
    what they are doing to avoid creating data integrity issues.

    For example:
        A screening form's validation check blocks the screening form
        from further edits because the subject's consent form has
        been submitted. The permission-based custom form feature can
        be used to bypass ALL validation on the screening form and
        allow the user to update the screening form.
    """

    # if custom_form_codename is None, this mixin does nothing
    custom_form_codename: str | None = None  # "e.g. edc_data_manager.special_bypassmodelform"

    def custom_modelform_factory(self):
        """Returns a basic modelform (with no validation checks)"""

        meta_cls = getattr(
            self.form,
            "Meta",
            type("Meta", (object,), {"model": self.model, "fields": "__all__"}),
        )

        class BasicModelForm(SiteModelFormMixin, forms.ModelForm):
            Meta = meta_cls

        BasicModelForm.__name__ = meta_cls.model.__name__ + "BasicForm"
        return BasicModelForm

    def get_form_cls(self, request):
        """Returns a custom Form class or the default.

        A custom Form class is returned if the user has the correct
        permissions otherwise returns the Form class originally
        declared on this ModelAdmin class.
        """
        if self.custom_form_codename and request.user.has_perm(self.custom_form_codename):
            try:
                messages.add_message(
                    request,
                    messages.WARNING,
                    format_html(
                        "<B>WARNING: All validation checks for this form have been disabled."
                        "</B><BR>Your user account includes the special permission "
                        f"`{self.custom_form_codename}`. <BR>Saving changes to this "
                        "form without validation may lead to serious data integrity errors. "
                        "<BR><B>If you did not expect this, contact your data manager "
                        "immediately and do not continue.</B>"
                    ),
                )
            except MessageFailure:
                pass
            form_cls = self.custom_modelform_factory()
        else:
            form_cls = self.form
        return form_cls

    def get_form(self, request, obj=None, change=False, **kwargs):
        """
        Return a Form class for use in the admin add view. This is used by
        add_view and change_view.

        EDC Note:
            The only change to this method is `get_form_cls` sets the
            `form_cls` variable instead of calling `self.form` throughout.
        """
        form_cls = self.get_form_cls(request)

        if "fields" in kwargs:
            fields = kwargs.pop("fields")
        else:
            fields = flatten_fieldsets(self.get_fieldsets(request, obj))
        excluded = self.get_exclude(request, obj)
        exclude = [] if excluded is None else list(excluded)
        readonly_fields = self.get_readonly_fields(request, obj)
        exclude.extend(readonly_fields)
        # Exclude all fields if it's a change form and the user doesn't have
        # the change permission.
        if (
            change
            and hasattr(request, "user")
            and not self.has_change_permission(request, obj)
        ):
            exclude.extend(fields)
        if excluded is None and hasattr(form_cls, "_meta") and form_cls._meta.exclude:
            # Take the custom ModelForm's Meta.exclude into account only if the
            # ModelAdmin doesn't define its own.
            exclude.extend(form_cls._meta.exclude)
        # if exclude is an empty list we pass None to be consistent with the
        # default on modelform_factory
        exclude = exclude or None

        # Remove declared form fields which are in readonly_fields.
        new_attrs = dict.fromkeys(f for f in readonly_fields if f in self.form.declared_fields)
        form = type(form_cls.__name__, (form_cls,), new_attrs)

        defaults = {
            "form": form,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
            **kwargs,
        }

        if defaults["fields"] is None and not modelform_defines_fields(defaults["form"]):
            defaults["fields"] = forms.ALL_FIELDS

        try:
            return modelform_factory(self.model, **defaults)
        except FieldError as e:
            raise FieldError(
                "%s. Check fields/fieldsets/exclude attributes of class %s."
                % (e, self.__class__.__name__)
            )
