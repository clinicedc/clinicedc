edc-model-admin
===============

Edc custom django ModelAdmin mixins, tags and templates


ModelAdminFormAutoNumberMixin
+++++++++++++++++++++++++++++

Overrides ModelAdmin's ``get_form`` to insert question numbers and the DB field names.


ModelAdminNextUrlRedirectMixin
++++++++++++++++++++++++++++++

Skips the ``changelist`` and redirects to the next CRF or Requisition listed in an edc visit schedule if "[Save and Next]"
is clicked instead of "[SAVE]"

.. code-block:: python

    class BaseModelAdmin:

        search_fields = ("subject_identifier",)
        add_form_template = "edc_model_admin/admin/change_form.html"
        change_form_template = "edc_model_admin/admin/change_form.html"
        change_list_template = "edc_model_admin/admin/change_list.html"

    @admin.register(CrfTwo)
    class CrfTwoAdmin(BaseModelAdmin, ModelAdminNextUrlRedirectMixin, admin.ModelAdmin):
        show_save_next = True
        show_cancel = True

You need to use the included ``change_form.html`` to override the submit buttons on the ``admin`` form.

See also:: ``edc_visit_schedule``


ModelAdminRedirectOnDeleteMixin
+++++++++++++++++++++++++++++++

Redirects the admin form on save to a view other than the default ``changelist`` if ``post_url_on_delete_name`` is set.

.. code-block:: python

    @admin.register(CrfFive)
    class CrfFiveAdmin(ModelAdminRedirectOnDeleteMixin, admin.ModelAdmin):

        post_url_on_delete_name = "dashboard2_app:dashboard_url"

        def post_url_on_delete_kwargs(self, request, obj):
            return {'subject_identifier': obj.subject_identifier}

You can also store url names in the request object if used together with the Middleware from ``edc_dashboard`` and ``edc_subject_dashboard``.
This is useful if you do not know the namespace until deployment.

For example, add to settings:

.. code-block:: python

    # ...
    MIDDLEWARE=[
        # ...,
        'edc_dashboard.middleware.DashboardMiddleware',
        'edc_subject_dashboard.middleware.DashboardMiddleware',
    ],
    DASHBOARD_URL_NAMES={
        'subject_dashboard_url': 'dashboard_app:subject_dashboard_url',
    },
    # ...

and then declare the model admin class:

.. code-block:: python

    @admin.register(CrfFive)
    class CrfFiveAdmin(ModelAdminRedirectOnDeleteMixin, admin.ModelAdmin):

        post_url_on_delete_name = "subject_dashboard_url"

        def post_url_on_delete_kwargs(self, request, obj):
            return {'subject_identifier': obj.subject_identifier}

``ModelAdminRedirectOnDeleteMixin`` will attempt to get the urlname from the request object using ``post_url_on_delete_name`` as a dictionary key.

Template themes
+++++++++++++++

You can change the default theme colors.

.. code-block:: python

    EDC_MODEL_ADMIN_CSS_THEME = "edc_indigo"

Options are:

* edc_indigo
* edc_deep_purple
* edc_purple

ModelForm Save Delay
++++++++++++++++++++
You can configure the save buttons on the CRF and PRN model forms to disable for a few seconds after clicked by the user.

.. code-block:: python

    # settings.py
    EDC_MODEL_ADMIN_SAVE_DELAY = 3000 # delay for 3 seconds

The default is 0 seconds.

Where internet connections are slow a user may think they did not click the save button and click it again.
This may lead to multiple submissions of the same form and raise an ``IntegrityError``.
Save delay disables the button for 3 seonds (or as configured) to minimize the chance of this type of
error occuring.

See also ``ModelAdminSubjectDashboardMixin`` and the ``change_form.html``.
