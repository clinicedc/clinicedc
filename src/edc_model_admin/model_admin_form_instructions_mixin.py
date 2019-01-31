class ModelAdminFormInstructionsMixin:
    """Add instructions to the add view context.

    Override the change_form.html to add instructions.

    Copy change_form.html from this apps templates/<app>/admin/ into
    /templates/admin/<your_app> or create a blank change_form.html in your
    /templates/admin/<your_app> folder and add this:

        {% extends "admin/change_form.html" %}
        {% block field_sets %}
            {% instructions %}
            {% additional_instructions %}
            {{ block.super }}
        {% endblock %}

    See also edc_admin_modify.py for the inclusion tags registered
    `instructions` and `additional_instructions` and the templates
    involved. These templates can be overridden just as django
    non-admin templates.
    """

    instructions = (
        "Please complete the form below. "
        "Required questions are in bold. "
        "When all required questions are complete click SAVE "
        "or, if available, SAVE NEXT. Based on your responses, "
        "additional questions may be "
        "required or some answers may need to be corrected."
    )
    add_instructions = None
    change_instructions = None

    additional_instructions = None
    add_additional_instructions = None
    change_additional_instructions = None

    def get_add_instructions(self, extra_context, request=None):
        extra_context = extra_context or {}
        extra_context["instructions"] = self.add_instructions or self.instructions
        extra_context["additional_instructions"] = (
            self.add_additional_instructions or self.additional_instructions
        )
        return extra_context

    def get_change_instructions(self, extra_context, request=None):
        extra_context = extra_context or {}
        extra_context["instructions"] = self.change_instructions or self.instructions
        extra_context["additional_instructions"] = (
            self.change_additional_instructions or self.additional_instructions
        )
        return extra_context

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = self.get_add_instructions(extra_context, request=request)
        return super().add_view(request, form_url=form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = self.get_change_instructions(extra_context, request=request)
        return super().change_view(
            request, object_id, form_url=form_url, extra_context=extra_context
        )
