edc-fieldsets
=============

ModelAdmin mixins to extend django.admin fieldsets atribute. The class ``Fieldset`` formats a data structure in the format of a django.fieldset.

For example:

.. code-block:: python

    from .fieldsets import fieldset, biosynex_fieldset


    @admin.register(BloodResult, site=ambition_subject_admin)
    class BloodResultsAdmin(CrfModelAdminMixin, admin.ModelAdmin):

        form = BloodResultForm

        conditional_fieldsets = {DAY1: biosynex_fieldset}

        fieldsets_move_to_end = [
            'Conclusion', 'Summary', 'Action', audit_fieldset_tuple[0]]

        fieldsets = fieldset

        radio_fields = ...


where ``fieldset`` is:


.. code-block:: python

    biosynex_fieldset = Fieldset(
        'bios_crag',
        'crag_control_result',
        'crag_t1_result',
        'crag_t2_result',
        section='BIOSYNEX® CryptoPS (Semi-quantitative CrAg)')

    fieldset = [(None, {'fields': ('subject_visit', 'report_datetime',)})]
    fieldset.append(('Conclusion', {
        'fields': ('results_abnormal', 'results_reportable')}))
    fieldset.append(
        ('Summary', {'classes': ('collapse', ), 'fields': ('summary', )}))
    fieldset.append(action_fieldset_tuple)
    fieldset.append(audit_fieldset_tuple)

The ``conditional_fieldsets`` will only display for CRF completed at visit ``DAY1``
