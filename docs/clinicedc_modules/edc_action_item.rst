edc-action-items
================

Add patient `action items` to the Edc

Overview
++++++++
Action items are reminders to submit a form.

Action items can be configured to drive data collection

* for forms that do not fit well in a visit schedule;
* for forms that are required based on some clinical event.

Action items are tracked. Each is allocated a unique `action_identifier` and maintain status (New, Open, Closed).

Actions can be chained. One action can create another action, group of actions or recreate itself.

Adverse Events, Death, OffSchedule are all good candidates.
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Adverse Event reports are required based on some clinical event. Since the event must be reported, leaving the decision to report to the user is not sufficient. An action item can be opened based on the clinical event and the status of the action item tracked administratively. The action item is associtaed with the AE report. Once the report is submitted, the action item closes. If additional data is required after an initial AE report is submitted, a follow-up action can automatically be opened.

See module `ambition-ae.action_items` for examples.

Defining action items
+++++++++++++++++++++

In the root of your App, define an `action_items` module. The edc-action-item site controller will `autodiscover` this module and `register` the action item classes.

Register action item classes in the `action_items` module like this

.. code-block:: python

    site_action_items.register(AeInitialAction)


A simple action item
++++++++++++++++++++

In it define actions using the ``Action`` class.

.. code-block:: python

    from edc_action_item.action import Action
    from edc_action_item.site_action_items import site_action_items
    from edc_constants.constants import HIGH_PRIORITY
    from ambition_ae.action_items import AeFollowupAction, AeTmgAction

    class AeInitialAction(Action):
        name = AE_INITIAL_ACTION
        display_name = 'Submit AE Initial Report'
        model = 'ambition_ae.aeinitial'
        show_on_dashboard = True
        instructions = 'Complete the initial report and forward to the TMG'
        priority = HIGH_PRIORITY

The action item is associated with its model

.. code-block:: python

    from edc_action_item.model_mixins import ActionModelMixin
    from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin

    class AeInitial(ActionModelMixin, NonUniqueSubjectIdentifierFieldMixin, BaseUuidModel):
        pass

    action_cls = AeInitialAction


Somewhere in your code, instantiate the action item

.. code-block:: python

    AeInitialAction(subject_identifier='12345')

This creates an `ActionItem` model instance for this subject with a `status` of `New` (if it does not exist).

Now create the associated model instance

.. code-block:: python

    field_options = {}
    AeInitial.objects.create(subject_identifier='12345', **field_options)

The `ActionItem` model instance now has a status of `Closed`.

Changing the criteria to close an action
++++++++++++++++++++++++++++++++++++++++

By default an action is closed once the associated model instance has been saved. For more refined behavior define `close_action_item_on_save` on the action item class


.. code-block:: python

    class AeInitialAction(Action):
        pass

    def close_action_item_on_save(self):
        self.delete_children_if_new(action_cls=self)
        return self.model_obj.report_status == CLOSED


Singleton action items
++++++++++++++++++++++

To ensure an action item does not create more than one instance per subject, use the `singleton` attribute.

.. code-block:: python

    class EnrollToSubstudyAction(Action):
        name = 'My Action'
        display_name = 'Enroll to sub-study'
        model = 'myapp.enroll'
        show_link_to_changelist = True
        admin_site_name = 'myapp_admin'
        priority = HIGH_PRIORITY
        create_by_user = False
        singleton=True


Action items that create a `next` action item
++++++++++++++++++++++++++++++++++++++++++++++

For an action item to open another action item(s) once closed, set `next_actions`.

.. code-block:: python

    class AeInitialAction(Action):

        name = AE_INITIAL_ACTION
        display_name = 'Submit AE Initial Report'
        model = 'ambition_ae.aeinitial'
        show_on_dashboard = True
        instructions = 'Complete the initial report and forward to the TMG'
        priority = HIGH_PRIORITY
        next_actions = [AeFollowupAction]

If the criteria for the next action is based on some other information declare `get_next_actions` on the action item and return the list of action items needed.

.. code-block:: python

    class AeInitialAction(Action):
        pass

    def get_next_actions(self):
        next_actions = []
        try:
            self.reference_model_cls().objects.get(
                ae_initial=self.model_obj.ae_initial)
        except MultipleObjectsReturned:
            pass
        else:
            if (self.model_obj.ae_initial.ae_classification
                    != self.model_obj.ae_classification):
                next_actions = [self]
        return next_actions


Action items with a notification
++++++++++++++++++++++++++++++++

An action item can be associated with a notification from ``edc_notification`` so that when an action is created a notification (email or sms) is sent to those registered to receive it.

A subclass of ``Action``, ``ActionWithNotification`` adds notifications to the action. The notification for the action is automatically registered when the action is registered by ``site_action_items``.

For example:

.. code-block:: python

    class AeTmgAction(ActionWithNotification):
        name = AE_TMG_ACTION
        display_name = "TMG AE Report pending"
        notification_display_name = "TMG AE Report"
        parent_action_names = [AE_INITIAL_ACTION],
        reference_model = "ambition_ae.aetmg"
        related_reference_model = "ambition_ae.aeinitial"
        related_reference_fk_attr = "ae_initial"
        show_link_to_changelist = True
        admin_site_name = "ambition_ae_admin"
