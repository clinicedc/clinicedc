edc_metadata
============

``edc-metadata`` puts a "metadata" layer on top of your data collection forms, namely CRFs and Requisitions. The "metadata" is used on the data entry dashboard (see also `edc_dashboard`). The metadata may be queried directly by a data manager to review the completion status of CRF and Requisition forms.

* Metadata is stored in two models, ``CrfMetaData`` and ``RequisitionMetaData``. One metadata record is created per form per visit. Metadata is only created for the data collection forms of a visit as defined in the ``visit schedule``.
* Metadata model instances are created for each visit when the ``visit`` model is saved. ``edc_metadata`` reads from the ``visit_schedule`` to decide which data collection form metadata model instances to create for a visit. (Note: See ``edc_visit_schedule``)
* Metadata is guaranteed to exist for every form defined in a visit after the visit form has been submitted.


``metadata`` model instances
----------------------------

Each  ``metadata`` model instance, ``CrfMetadata`` or ``RequisitionMetadata``, is managed by
an actual CRF or REQUISITION model listed in the ``visit_schedule``.
``CrfMetadata` model instances are created for each CRF listed in the visit schedule. That is,
if the visit schedule schedules a CRF for 5 different visits, 5 ``CrfMetadata` model instances
will eventually be created. Metadata model instances are created when the ``visit`` model for a
timepoint is saved.
When you  ``save`` a CRF within a visit, the ``entry_status`` of the the metadata instance`s
it manages is updated from ``REQUIRED`` to ``KEYED``.

    The same applies to ``RequisitionMetadata`` for REQUISITIONS.

Entry status
------------

By default the ``entry_status`` field attribute is set to ``REQUIRED``. You can change the default of each CRF to ``NOT_REQUIRED`` in your declaration in the visit schedule.  See ``visit_schedule.crf``.

    The same applies to REQUISITIONS.


``metadata_rules`` manipulate ``metadata`` model instances
----------------------------------------------------------

``metadata_rules`` are declared to manipulate ``metadata`` model instances. The rules change the ``entry_status`` field attribute from ``REQUIRED`` to ``NOT_REQUIRED`` or visa-versa.
If the manager of the metadata instance, the CRF or REQUISITION model instance, exists, the entry status is updated to ``KEYED``and the ``metadata_rules`` targeting the metadata instance are ignored.
``metadata rules`` are run on each ``save`` of the visit and managing model instances.
If a value on some other form implies that your form should not be completed, your form`s metadata "entry_status" will change from REQUIRED to NOT REQUIRED upon ``save`` of the other form.
Metadata is ``updated`` through a ``post_save`` signal that re-runs the ``metadata rules``.

    See also ``edc_metadata_rules``


Getting started
---------------

Models: Visit, Crfs and Requisitions
++++++++++++++++++++++++++++++++++++

Let`s prepare the models that will be used in the scheduled data collection. These models are your visit models, crf models and requisition models.

Your application also has one or more ``Visit`` models. Each visit model is declared with the ``CreatesMetadataModelMixin``:

.. code-block:: python

    class SubjectVisit(CreatesMetadataModelMixin, PreviousVisitMixin, VisitModelMixin,
                       RequiresConsentModelMixin, BaseUuidModel):

        appointment = models.OneToOneField(Appointment)

        class Meta(RequiresConsentModelMixin.Meta):
            app_label = 'example'

Your ``Crf`` models are declared with the ``CrfModelMixin``:

.. code-block:: python

    class CrfOne(CrfModelMixin, BaseUuidModel):

        subject_visit = models.ForeignKey(SubjectVisit)

        f1 = models.CharField(max_length=10, default='erik')

        class Meta:
            app_label = 'example'

Your ``Requisition`` models are declared with the ``RequisitionModelMixin``:

.. code-block:: python

    class SubjectRequisition(RequisitionModelMixin, BaseUuidModel):

        subject_visit = models.ForeignKey(SubjectVisit)

        f1 = models.CharField(max_length=10, default='erik')

        class Meta:
            app_label = 'example'

metadata_rules
--------------

As described above, ``metadata_rules`` manipulate the ``entry_status`` of CRF and Requisition ``metadata``. ``metadata_rules`` are registered to ``site_metadata_rules`` in module ``metadata_rules.py``. Place this file in the root of your app. Each app can have one ``metadata_rules.py``.

 See also ``edc_metadata_rules``

autodiscovering metadata_rules
++++++++++++++++++++++++++++++

AppConfig will ``autodiscover`` the rule files and print to the console whatever it finds:

* checking for metadata_rules ...
* registered metadata_rules from application 'edc_example'

Inspect metadata_rules
----------------------

Inspect ``metadata_rules`` from the site registry:

.. doctest:: metadata-rules

    >>> from edc_metadata.rules.site_metadata_rules import site_metadata_rules

    >>> for rule_groups in site_metadata_rules.registry.values():
    ...    for rule_group in rule_groups:
    ...        print(rule_group._meta.rules)

    (<edc_example.rule_groups.ExampleRuleGroup: crfs_male>, <edc_example.rule_groups.ExampleRuleGroup: crfs_female>)
    (<edc_example.rule_groups.ExampleRuleGroup2: bicycle>, <edc_example.rule_groups.ExampleRuleGroup2: car>)

Writing metadata_rules
----------------------

``metadata_rules`` are declared in a ``RuleGroup``. The syntax is similar to the ``django``
model class.

Let`s start with an example from the perspective of the person entering subject data.
On a dashboard there are 4 forms (models) to complete. The "rule" is that if the subject
is male, only the first two forms should be complete. If the subject is female, only the
last two forms should be complete. So the metadata should show:

**Subject is Male:**

* crf_one - REQUIRED, link to entry screen available
* crf_two - REQUIRED, link to entry screen available
* crf_three - NOT REQUIRED, link to entry screen not available
* crf_four - NOT REQUIRED, link to entry screen not available

**Subject is Female:**

* crf_one - NOT REQUIRED
* crf_two - NOT REQUIRED
* crf_three - REQUIRED
* crf_four - REQUIRED

A ``Rule`` that changes the ``metadata`` if the subject is male would look like this:

.. code-block:: python

    crfs_male = CrfRule(
        predicate=P('gender', 'eq', 'MALE'),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=['crfone', 'crftwo'])

The rule above has a ``predicate`` that evaluates to True or not. If ``gender`` is equal
to ``MALE`` the consequence is ``REQUIRED``, else ``NOT_REQUIRED``. For this rule, for a
MALE, the metadata ``entry_status`` for ``crf_one`` and ``crf_two`` will be updated to
``REQUIRED``. For a FEMALE both will be set to ``NOT_REQUIRED``.

Rules are declared as attributes of a RuleGroup much like fields in a ``django`` model:

.. code-block:: python

    @register()
    class ExampleRuleGroup(CrfRuleGroup):

        crfs_male = CrfRule(
            predicate=P('gender', 'eq', 'MALE'),
            consequence=REQUIRED,
            alternative=NOT_REQUIRED,
            target_models=['crfone', 'crftwo'])

        crfs_female = CrfRule(
            predicate=P('gender', 'eq', FEMALE),
            consequence=REQUIRED,
            alternative=NOT_REQUIRED,
            target_models=['crfthree', 'crffour'])

        class Meta:
            app_label = 'edc_example'

``RuleGroup`` class declarations are placed in file ``metadata_rules.py`` in the root of
your application. They are registered in the order in which they appear in the file. All rule
groups are available from the ``site_metadata_rules`` global.

    **IMPORTANT** If the related visit model (e.g. SubjectVisit) has a different ``app_label`` than
    ``Meta.app_label``, a ``RuleGroupError`` will be raised because the ``RuleGroup`` assumes
    the app_labels are the same. To avoid this, specify the related visit model ``label_lower``
    on ``Meta``.

For example:

.. code-block:: python

    @register()
    class ExampleRuleGroup(CrfRuleGroup):

        crfs_male = CrfRule(
            predicate=P('gender', 'eq', 'MALE'),
            consequence=REQUIRED,
            alternative=NOT_REQUIRED,
            target_models=['crfone', 'crftwo'])

        class Meta:
            app_label = 'edc_example'
            related_visit_model = "edc_visit_tracking.subjectvisit"

Inheritance
-----------

When using single inheritance, set Meta class `abstract` on the base class:

.. code-block:: python

    class ExampleRuleGroup(CrfRuleGroup):

        crfs_male = CrfRule(
            predicate=P('gender', 'eq', 'MALE'),
            consequence=REQUIRED,
            alternative=NOT_REQUIRED,
            target_models=['crfone', 'crftwo'])

        class Meta:
            abstract = True


    class MyRuleGroup(ExampleRuleGroup):
        class Meta:
            app_label = 'edc_example'
            related_visit_model = "edc_visit_tracking.subjectvisit"


More on Rules
-------------

The rule ``consequence`` and ``alternative`` accept these values:

.. code-block:: python

    from edc_metadata.constants import REQUIRED, NOT_REQUIRED
    from edc_metadata.rules.constants import DO_NOTHING

* REQUIRED
* NOT_REQUIRED
* DO_NOTHING

It is recommended to write the logic so that the ``consequence`` is REQUIRED if the
``predicate`` evaluates to  ``True``.

In the examples above, the rule ``predicate`` can only access values that can be found
on the subjects`s current ``visit`` instance or ``registered_subject`` instance. If the
value you need for the rule ``predicate`` is not on either of those instances, you can
pass a ``source_model``. With the ``source_model`` declared you would have these data
available:

* current visit model instance
* registered subject (see ``edc_registration``)
* source model instance for the current visit

Let`s say the rules changes and instead of refering to ``gender`` (male/female) you wish
to refer to the value field of ``favorite_transport`` on model ``CrfTransport``.
``favorite_transport`` can be "car" or "bicycle". You want the first rule ``predicate``
to read as:

* If ``favorite_transport`` is equal to ``bicycle`` then set the metadata ``entry_status`` for ``crf_one`` and ``crf_two`` to REQUIRED, if not, set both to NOT_REQUIRED

and the second to read as:

* If ``favorite_transport`` is equal to ``car`` then set the metadata ``entry_status`` for ``crf_three`` and ``crf_four`` to REQUIRED, if not, set both to NOT_REQUIRED.

The field for car/bicycle, ``favorite_transport`` is on model ``CrfTransport``. The
RuleGroup might look like this:

.. code-block:: python

    @register()
    class ExampleRuleGroup(RuleGroup):

        bicycle = CrfRule(
            predicate=P('favorite_transport', 'eq', 'bicycle'),
            consequence=REQUIRED,
            alternative=NOT_REQUIRED,
            target_models=['crfone', 'crftwo'])

        car = CrfRule(
            predicate=P('favorite_transport', 'eq', car),
            consequence=REQUIRED,
            alternative=NOT_REQUIRED,
            target_models=['crfthree', 'crffour'])

        class Meta:
            app_label = 'edc_example'
            source_model = 'CrfTransport'

Note that ``CrfTransport`` is a ``crf`` model in the Edc. That is, it has a ``foreign key``
to the visit model. Internally the query will be constructed like this:

.. code-block:: python

    # source model instance for the current visit
    visit_attr = 'subject_visit'
    source_obj = CrfTansport.objects.get(**{visit_attr: visit})

    # queryset of source model for the current subject_identifier
    visit_attr = 'subject_visit'
    source_qs = CrfTansport.objects.filter(**{'{}__subject_identifier'.format(visit_attr): subject_identifier})

* If the source model instance does not exist, the rules in the rule group will not run.
* If the target model instance exists, no rule can change it`s metadata from KEYED.

More Complex Rule Predicates
----------------------------

There are two provided classes for the rule ``predicate``, ``P`` and ``PF``. With ``P`` you
can make simple rule predicates like those used in the examples above. All standard opertors
can be used.

For example:

.. code-block:: python

    predicate = P('gender', 'eq', 'MALE')
    predicate = P('referral_datetime', 'is not', None)
    predicate = P('age', '<=', 64)

If the logic needs to a bit more complicated, the ``PF`` class allows you to pass a ``lambda`` function directly:

.. code-block:: python

    predicate = PF('age', func=lambda x: True if x >= 18 and x <= 64 else False)

    predicate = PF('age', 'gender', func=lambda x, y: True if x >= 18 and x <= 64 and y == MALE else False)


Rule predicates as functions
----------------------------

If the logic needs to be more complicated than is recommended for a simple lambda, you can
just pass a function. When writing your function just remember that the rule ``predicate``
must always evaluate to True or False.

The function will be called with:

* ``visit``: the related_visit model instance
* ``registered_subject``: the instance for the current subject
* ``source_obj``: the model instance who triggered the post_save signal
* ``source_qs``

.. code-block:: python

    def my_func(visit, registered_subject, source_obj, source_qs) -> bool:
        if registered_subject.age_in_years >= 18 and registered_subject.gender == FEMALE:
            return True
        return False

The function is then called on the RuleGroup like this:

.. code-block:: python

    @register()
    class ExampleRuleGroup(RuleGroup):

        some_rule = CrfRule(
            predicate=my_func,
            consequence=REQUIRED,
            alternative=NOT_REQUIRED,
            target_models=['crfone', 'crftwo'])

        class Meta:
            app_label = 'edc_example'
            source_model = 'CrfTransport'

Grouping rule predicate functions with ``PredicateCollection``
--------------------------------------------------------------

If you have many ``RuleGroups`` and predicate functions, it is useful to collect your predicate functions into a class:

.. code-block:: python

    class Predicates:
        household_head_model = "edc_he.healtheconomicshouseholdhead"
        patient_model = "edc_he.healtheconomicspatient"

        @property
        def hoh_model_cls(self):
            return django_apps.get_model(self.household_head_model)

        @property
        def patient_model_cls(self):
            return django_apps.get_model(self.patient_model)

        def patient_required(self, visit, **kwargs) -> bool:
            required = False
            if (
                self.hoh_model_cls.objects.filter(
                    subject_visit__subject_identifier=visit.subject_identifier
                ).exists()
                and not self.patient_model_cls.objects.filter(
                    subject_visit__subject_identifier=visit.subject_identifier
                ).exists()
            ):
                required = hoh_obj.hoh == YES
            return required


then you might do something like this in your ``metadata_rules`` module:

.. code-block:: python

    pc = Predicates()

    @register()
    class ExampleRuleGroup(RuleGroup):

        some_rule = CrfRule(
            predicate=pc.household_head_required,
            consequence=REQUIRED,
            alternative=NOT_REQUIRED,
            target_models=['healtheconomicshouseholdhead'])

        some_other_rule = CrfRule(
            predicate=pc.patient_required,
            consequence=REQUIRED,
            alternative=NOT_REQUIRED,
            target_models=['healtheconomicspatient'])

        class Meta:
            app_label = 'edc_he'
            source_model = "edc_he.healtheconomics"
            related_visit_model = "edc_visit_tracking.subjectvisit"

Setting a custom ``PredicateCollection`` for a RuleGroup using Meta
-------------------------------------------------------------------

If a ``RuleGroup`` has its own ``Predicate`` class you can declare it on the ``Meta`` class. Set the ``predicate`` attribute to the name of the function to call.

.. code-block:: python

    @register()
    class ExampleRuleGroup(RuleGroup):

        some_rule = CrfRule(
            predicate="household_head_required",
            consequence=REQUIRED,
            alternative=NOT_REQUIRED,
            target_models=['healtheconomicshouseholdhead'])

        some_other_rule = CrfRule(
            predicate="patient_required",
            consequence=REQUIRED,
            alternative=NOT_REQUIRED,
            target_models=['healtheconomicspatient'])

        class Meta:
            app_label = 'edc_he'
            source_model = "edc_he.healtheconomics"
            related_visit_model = "edc_visit_tracking.subjectvisit"
            predicates = Predicates()


Rule Group Order
----------------

    **IMPORTANT**: RuleGroups are evaluated in the order they are registered and the rules within each rule group are evaluated in the order they are declared on the RuleGroup.

Rule evaluation internals
-------------------------

Understanding how rules are evaluated internally helps when diagnosing unexpected
``entry_status`` values or writing new rules.

**Evaluation chain**

When rules are triggered (by a visit or CRF ``post_save`` signal), the chain is:

1. ``MetadataRuleEvaluator`` (``metadata_rules/metadata_rule_evaluator.py``) — the entry
   point. Looks up all registered ``RuleGroups`` for the visit model's ``app_label`` and
   calls ``evaluate_rules()`` on each in registration order.

2. ``CrfRuleGroup.evaluate_rules()`` (``metadata_rules/crf/crf_rule_group.py``) — iterates
   through each rule on the group. For each rule it:

   a. **Skips** the rule entirely if the ``source_model`` is not the visit model itself and
      is not in the set of CRFs scheduled for this visit (including PRNs and, for unscheduled
      visits, ``crfs_unscheduled`` + ``crfs_prn``).
   b. Calls ``rule.run(related_visit)`` to evaluate the predicate and determine
      ``entry_status``.
   c. For each ``target_model``, skips the update if the target is not in the visit's CRFs.
   d. Calls ``MetadataUpdater.get_and_update()`` to apply the result.

3. ``MetadataUpdater`` (``metadata_updater.py``) — retrieves the metadata record via
   ``MetadataHandler``, then updates ``entry_status`` (and timestamp fields) if it differs
   from the current value. If the source model instance already exists (is ``KEYED``), the
   ``entry_status`` is forced to ``KEYED`` regardless of the rule result.

4. ``MetadataHandler`` (``metadata_handler.py``) — fetches the metadata record. If it does
   not exist, it creates it by finding the CRF in ``visit.all_crfs`` and calling
   ``Creator.create_crf()``. Creation is skipped for missed visits.

**Source model scoping**

A ``RuleGroup``'s ``source_model`` determines when the group runs:

* If ``source_model`` is the visit model (e.g. ``SubjectVisit``), the rules run on every
  visit save.
* If ``source_model`` is a CRF (e.g. ``SignsAndSymptoms``), the rules only run when that
  CRF is in the current visit's CRF list. This means the same ``RuleGroup`` may silently
  skip at visits where that CRF is not scheduled.

**KEYED records are never changed by rules**

If the target CRF has already been submitted (``entry_status == KEYED``), no rule can
change its ``entry_status``. ``MetadataUpdater.get_and_update()`` detects this and
forces ``entry_status`` to ``KEYED``, overriding the rule result.

**Singleton CRFs — ``PersistantSingletonMixin``**

For CRF models that should be entered exactly once across the entire schedule (singletons),
the ``PersistantSingletonMixin`` (``metadata_rules/persistant_singleton_mixin.py``) can be
included in your ``Predicates`` class. Its ``persistant_singleton_required()`` method:

* Returns ``True`` (REQUIRED) only for the **last attended scheduled visit** where the
  singleton has not yet been submitted, and only if the visit code is not in the
  ``exclude_visit_codes`` list.
* Calls ``set_other_crf_metadata_not_required()`` to set all other timepoints for that
  singleton to ``NOT_REQUIRED``, keeping the "required" marker at the last attended visit
  as the subject progresses through the schedule.
* Once submitted, sets all non-``KEYED`` instances to ``NOT_REQUIRED``.

For singletons, a separate ``post_save`` signal
(``metadata_update_previous_timepoints_for_singleton_on_post_save`` in ``signals.py``)
walks back through all previous appointments and re-runs metadata rules with
``allow_create=False`` whenever a singleton CRF is saved.

**Key classes summary**

.. list-table::
   :header-rows: 1

   * - Class / file
     - Role
   * - ``metadata_rules/metadata_rule_evaluator.py`` — ``MetadataRuleEvaluator``
     - Entry point; iterates registered rule groups for the visit model's app label
   * - ``metadata_rules/crf/crf_rule_group.py`` — ``CrfRuleGroup``
     - Scopes rules to the visit's CRF list; calls ``MetadataUpdater`` per target model
   * - ``metadata_rules/rule.py`` — ``Rule``
     - Runs the predicate via ``RuleEvaluator`` and returns ``{target_model: entry_status}``
   * - ``metadata_rules/rule_evaluator.py`` — ``RuleEvaluator``
     - Evaluates the predicate (``P``, ``PF``, or callable) and returns the consequence
       or alternative
   * - ``metadata_updater.py`` — ``MetadataUpdater``
     - Fetches metadata via ``MetadataHandler`` and applies the new ``entry_status``
   * - ``metadata_handler.py`` — ``MetadataHandler``
     - Gets or creates the metadata record; creation uses ``Creator.create_crf()``
   * - ``metadata_rules/persistant_singleton_mixin.py`` — ``PersistantSingletonMixin``
     - Predicate helper for singleton CRFs; keeps ``REQUIRED`` at the last attended visit

Updating metadata
-----------------

It is a good idea to updata metadata after code changes and data migrations. To do so just
run the management command:

.. code-block:: bash

    python manage.py update_metadata

Testing
-------

Since the order in which rules run matters, it is essential to test the rules together. See
``tests`` for some examples. When writing tests it may be helpful to know the following:

* the standard Edc model configuration assumes you have consent->enrollment->appointments->visit->crfs and requisitions.
* rules can be instected after boot up in the global registry ``site_metadata_rules``.
* all rules are run when the visit  is saved.

More examples
-------------

See ``edc_example`` for working RuleGroups and how models are configured with the ``edc_metadata`` mixins. The ``tests`` in ``edc_metadata.rules`` use the rule group and model classes in ``edc_example``.


Notes on clinicedc
------------------

The standard clinicedc model configuration assumes you have a data entry flow like this:::

    consent->enrollment->appointment->visit (1000)->crfs and requisitions
                         appointment->visit (2000)->crfs and requisitions
                         appointment->visit (3000)->crfs and requisitions
                         appointment->visit (4000)->crfs and requisitions

You should also see the other dependencies, ``edc_consent``, ``edc_visit_schedule``, ``edc_appointment``, ``edc_visit_tracking``, ``edc_metadata``, etc.

Signals
-------

In the ``signals`` file:

**visit model ``post_save``:**

* Metadata is created for a particular visit and visit code, e.g. 1000, when the ``visit`` model is saved for a subject and visit code using the default ``entry_status`` configured in the ``visit_schedule``.
* Immediately after creating metadata, all rules for the ``app_label`` are run in order. The ``app_label`` is the ``app_label`` of the visit model.

**crf or requisition model ``post_save``:**

* the metadata instance for the crf/requisition is updated and then all rules are run.

**crf or requisition model ``post_delete``:**

* the metadata instance for the crf/requisition is reset to the default ``entry_status`` and then all rules are run.

Metadata creation and regeneration internals
--------------------------------------------

Metadata records are created, updated, and deleted through several coordinated mechanisms.
Understanding these is useful when diagnosing performance issues or writing data migrations.

**Normal flow (signal-driven)**

When a ``visit`` model is saved, ``metadata_create_on_post_save()`` in ``signals.py`` calls
``instance.metadata_create()`` on the visit. This is provided by ``CreatesMetadataModelMixin``
(``model_mixins/creates/creates_metadata_model_mixin.py``) and delegates to
``Metadata.prepare()`` in ``metadata/metadata.py``.

``Metadata.prepare()`` runs in two steps:

1. ``Destroyer.delete()`` — deletes all ``REQUIRED`` and ``NOT_REQUIRED`` metadata for the visit
   (``KEYED`` records are left intact).
2. ``Creator.create()`` — iterates through all CRFs and requisitions in the visit schedule and
   calls ``CrfCreator`` or ``RequisitionCreator`` for each, which uses ``get_or_create`` with
   ``IntegrityError`` handling for race conditions.

When a CRF or requisition is saved, ``metadata_update_on_post_save()`` updates the single
corresponding metadata record's ``entry_status`` to ``KEYED`` and re-runs metadata rules.

When a CRF or requisition is deleted, ``metadata_reset_on_post_delete()`` resets the
``entry_status`` back to its default and re-runs metadata rules.

**Bulk regeneration (management command)**

The ``update_metadata`` management command (``management/commands/update_metadata.py``) is used
after code changes or data migrations to rebuild all metadata from scratch:

.. code-block:: bash

    python manage.py update_metadata

It works as follows:

1. Deletes **all** ``CrfMetadata`` and ``RequisitionMetadata`` records.
2. Instantiates ``MetadataRefresher`` (``metadata_refresher.py``) and calls ``.run()``.
3. ``MetadataRefresher.create_or_update_metadata_for_all()`` iterates through every visit
   model instance and calls ``metadata_create()`` on each, recreating metadata per the
   current visit schedule.
4. After creation, ``MetadataRefresher`` removes orphaned metadata records — those whose
   ``model`` is no longer listed in the visit schedule or registered in admin — via
   ``verifying_crf_metadata_with_visit_schedule_and_admin()`` and its requisition equivalent.
5. Finally, ``MetadataRefresher.run_metadata_rules()`` iterates through all source model
   instances and re-runs all metadata rules.

**Key classes and files**

.. list-table::
   :header-rows: 1

   * - Class / file
     - Purpose
   * - ``metadata/metadata.py`` — ``Metadata``
     - Orchestrates ``Destroyer`` + ``Creator`` for a single visit
   * - ``metadata/metadata.py`` — ``Creator``
     - Creates ``CrfMetadata`` / ``RequisitionMetadata`` for all forms in a visit
   * - ``metadata/metadata.py`` — ``CrfCreator``
     - ``get_or_create`` for a single ``CrfMetadata`` record
   * - ``metadata/metadata.py`` — ``Destroyer``
     - Deletes non-``KEYED`` metadata for a visit before recreation
   * - ``metadata_refresher.py`` — ``MetadataRefresher``
     - Bulk rebuild across all visits; removes orphaned records
   * - ``model_mixins/creates/creates_metadata_model_mixin.py`` — ``CreatesMetadataModelMixin``
     - Mixin on the visit model; entry point for signal-driven creation
   * - ``update_metadata_on_schedule_change.py`` — ``UpdateMetadataOnScheduleChange``
     - Bulk-updates ``schedule_name`` / ``visit_schedule_name`` on existing records when
       schedule configuration changes
