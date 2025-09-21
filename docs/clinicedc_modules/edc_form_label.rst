edc-form-label
==============
Customize Django's form label in realtime

For a sequence of data collection timepoints, we ask the question, "Are you circumcised?". At some time point we hope the response will be `YES`, but until then, we need to ask "Since we last saw you, were you circumcised?". It is a lot better if we can ask, "Since we last saw you in 'October 2018', were you circumcised?", where 'October 2018' represents the timepoint from which we got our last reponse.

This module shows how you can insert 'October 2018' into the ModelAdmin/ModelForm the form label in realtime.


For example:

For a sequence of data collection timepoints, we ask the question, "Are you circumcised". At some point we hope the  response will be YES. But until then we need to ask "Since we last saw you in October 2018, were you circumcised?", etc.

.. code-block:: python

    from edc_form_label import FormLabel, CustomFormLabel, FormLabelModelAdminMixin

    class MyCustomLabelCondition(CustomLabelCondition):
        def check(self, **kwargs):
            if self.previous_obj.circumcised == NO:
                return True
            return False


    @register(MyModel)
    class MyModelAdmin(FormLabelModelAdminMixin, admin.ModelAdmin):

        fieldsets = (
            (None, {
                'fields': (
                    'subject_visit',
                    'report_datetime',
                    'circumcised')},
             ),
        )

        custom_form_labels = [
            FormLabel(
                field='circumcised',
                custom_label='Since we last saw you in {previous_visit}, were you circumcised?',
                condition_cls=MyCustomLabelCondition)
        ]
