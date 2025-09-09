Capturing results
=================

Simple blood result data collection format for django models

In this design
    * a specimen requisition for a panel is completed first (SubjectRequisition)
    * result is received and entered into a result form
    * if a result is admnormal or gradable, an ActionItem is created.

Building the Model
------------------

Below we create a model class with ``BloodResultsModelMixin``. On the class we specify the ``lab_panel`` and limit the FK the requisitions of this panel using ``limit_choices_to``.

.. code-block:: python

    # models.py

    from edc_lab.model_mixins import CrfWithRequisitionModelMixin, requisition_fk_options
    from edc_lab_panels.panels import chemistry_panel

    class BloodResultsFbc(
        CrfWithRequisitionModelMixin,
        BloodResultsModelMixin,
        BaseUuidModel,
    ):

        lab_panel = fbc_panel

        requisition = models.ForeignKey(
            limit_choices_to={"panel__name": fbc_panel.name}, **requisition_fk_options
        )

        class Meta(CrfWithActionModelMixin.Meta, BaseUuidModel.Meta):
            verbose_name = "Blood Result: FBC"
            verbose_name_plural = "Blood Results: FBC"

The above example has no fields for results, so let's add some model mixins, one for each result item.

.. code-block:: python

    # models.py

    class BloodResultsFbc(
        CrfWithRequisitionModelMixin,
        HaemoglobinModelMixin,
        HctModelMixin,
        RbcModelMixin,
        WbcModelMixin,
        PlateletsModelMixin,
        MchModelMixin,
        MchcModelMixin,
        McvModelMixin,
        BloodResultsModelMixin,
        CrfStatusModelMixin,
        BaseUuidModel,
    ):

        lab_panel = fbc_panel

        requisition = models.ForeignKey(
            limit_choices_to={"panel__name": fbc_panel.name}, **requisition_fk_options
        )

        class Meta(CrfWithActionModelMixin.Meta, BaseUuidModel.Meta):
            verbose_name = "Blood Result: FBC"
            verbose_name_plural = "Blood Results: FBC"

If an ``ActionItem`` is to be created because of an abnormal or reportable result item, add the ActionItem.

.. code-block:: python

    # models.py

    class BloodResultsFbc(
        CrfWithActionModelMixin,
        CrfWithRequisitionModelMixin,
        HaemoglobinModelMixin,
        HctModelMixin,
        RbcModelMixin,
        WbcModelMixin,
        PlateletsModelMixin,
        MchModelMixin,
        MchcModelMixin,
        McvModelMixin,
        BloodResultsModelMixin,
        CrfStatusModelMixin,
        BaseUuidModel,
    ):
        action_name = BLOOD_RESULTS_FBC_ACTION

        lab_panel = fbc_panel

        requisition = models.ForeignKey(
            limit_choices_to={"panel__name": fbc_panel.name}, **requisition_fk_options
        )

        class Meta(CrfWithActionModelMixin.Meta, BaseUuidModel.Meta):
            verbose_name = "Blood Result: FBC"
            verbose_name_plural = "Blood Results: FBC"

Building the ModeForm class
---------------------------
The ModelForm class just needs the Model class and the panel. In this case ``BloodResultsFbc`` and ``fbc_panel``.

.. code-block:: python

    # forms.py

    class BloodResultsFbcFormValidator(BloodResultsFormValidatorMixin, CrfFormValidator):
        panel = fbc_panel


    class BloodResultsFbcForm(ActionItemCrfFormMixin, CrfModelFormMixin, forms.ModelForm):
        form_validator_cls = BloodResultsFbcFormValidator

        class Meta(ActionItemCrfFormMixin.Meta):
            model = BloodResultsFbc
            fields = "__all__"


Building the ModelAdmin class
-----------------------------

The ModelAdmin class needs the Model class, ModelForm class and the panel.

.. code-block:: python

    # admin.py

    @admin.register(BloodResultsFbc, site=intecomm_subject_admin)
    class BloodResultsFbcAdmin(BloodResultsModelAdminMixin, CrfModelAdmin):
        form = BloodResultsFbcForm
        fieldsets = BloodResultFieldset(
            BloodResultsFbc.lab_panel,
            model_cls=BloodResultsFbc,
            extra_fieldsets=[(-1, action_fieldset_tuple)],
        ).fieldsets


The SubjectRequistion ModelAdmin class
--------------------------------------

When using ``autocomplete`` for the subject requsition FK on the result form ModelAdmin class, the subject requsition model admin class needs to filter the search results passed to the autocomplete control.

If all result models are prefixed with "bloodresult", you can filter on the path name like this:

.. code-block:: python

    # admin.py

    @admin.register(SubjectRequisition, site=intecomm_subject_admin)
    class SubjectRequisitionAdmin(RequisitionAdminMixin, CrfModelAdmin):
        form = SubjectRequisitionForm

        # ...

        def get_search_results(self, request, queryset, search_term):
            queryset, use_distinct = super().get_search_results(request, queryset, search_term)
            path = urlsplit(request.META.get("HTTP_REFERER")).path
            query = urlsplit(request.META.get("HTTP_REFERER")).query
            if "bloodresult" in str(path):
                attrs = parse_qs(str(query))
                try:
                    subject_visit = attrs.get("subject_visit")[0]
                except (TypeError, IndexError):
                    pass
                else:
                    queryset = queryset.filter(subject_visit=subject_visit, is_drawn=YES)
            return queryset, use_distinct

