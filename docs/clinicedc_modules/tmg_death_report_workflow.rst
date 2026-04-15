TMG Death Report Workflow
=========================

This document describes the action-item workflow used by ``edc_adverse_event``
to manage death-report review by the Trial Management Group (TMG).

Overview
++++++++

The workflow coordinates three models through ``edc_action_item`` action
classes:

* ``DeathReport`` — the original death report, submitted by the site.
* ``DeathReportTmg`` — the first TMG reviewer's independent assessment.
* ``DeathReportTmgSecond`` — a proxy of ``DeathReportTmg``, used by a
  second independent TMG reviewer when the first reviewer disagrees with
  the site's cause of death.

All TMG action items are created by the system (``create_by_user = False``)
and are ``singleton`` — they appear automatically in the reviewer's queue
rather than being added manually.

TMG reviewers do not navigate to these reports through the normal subject
dashboard. They access them from the **TMG Listboard**, a dedicated area
of the site provided by ``edc_adverse_event``. Access is gated by
permissions assigned to two groups defined in
``edc_adverse_event.auths``:

* ``TMG`` — full review and edit access.
* ``TMG_REVIEW`` — view-only access.

The key codenames are ``edc_adverse_event.view_tmg_listboard`` (listboard
access) and ``edc_adverse_event.nav_tmg_section`` (navbar visibility). A
user must be assigned a role that includes one of these groups to see
or use the TMG Listboard.

The listboard itself is composed of several views under
``edc_adverse_event.views.tmg``:

* ``NewTmgAeListboardView`` / ``OpenTmgAeListboardView`` /
  ``ClosedTmgAeListboardView`` — AE TMG action items grouped by status.
* ``DeathListboardView`` — TMG death reports.

These views surface the action items for ``AE_TMG_ACTION``,
``DEATH_REPORT_TMG_ACTION`` and ``DEATH_REPORT_TMG_SECOND_ACTION``,
filtered by ``NEW`` / ``OPEN`` / ``CLOSED`` status, so reviewers can pick
up new work, continue in-progress reviews, or audit closed reports from
one place.

Step-by-step
++++++++++++

1. **DeathReport is submitted.**
   ``DeathReportAction`` is typically scheduled as a next-action from
   ``AeInitialAction`` or ``AeFollowupAction`` when the outcome is death
   or the AE is grade 5.

2. **First TMG review is scheduled.**
   On save of ``DeathReport``, ``DeathReportAction.get_next_actions``
   schedules a single ``DEATH_REPORT_TMG_ACTION`` (if one does not already
   exist for the same parent/related action item) and an
   ``END_OF_STUDY_ACTION`` if the participant is not already off study.

3. **First TMG reviewer completes DeathReportTmg.**
   The reviewer records their own assessment of the cause of death and
   sets the boolean field ``cause_of_death_agreed`` to indicate whether
   they agree with the cause recorded on the original ``DeathReport``.

4. **Disagreement triggers a second review.**
   In ``DeathReportTmgAction.get_next_actions``, if
   ``cause_of_death_agreed == NO`` a ``DEATH_REPORT_TMG_SECOND_ACTION`` is
   scheduled, queuing a ``DeathReportTmgSecond`` for an independent second
   reviewer. Note that the trigger is the explicit boolean field — there
   is no programmatic comparison of cause-of-death values between the two
   reports.

5. **Agreement cleans up any pending second review.**
   In ``DeathReportTmgAction.close_action_item_on_save``, if
   ``cause_of_death_agreed == YES`` any ``new`` child second-review action
   items are removed via ``delete_children_if_new``. This handles the case
   where the first reviewer toggles from NO back to YES before closing.

6. **Close and reopen semantics.**
   Both ``DeathReportTmgAction`` and ``DeathReportTmgSecondAction`` close
   only when the reference object's ``report_status == CLOSED``. Saves to
   a non-closed report can reopen the action item; once ``CLOSED``,
   subsequent changes will not reopen it
   (``reopen_action_item_on_change`` returns ``False``).

Relevant classes
++++++++++++++++

* ``edc_adverse_event.action_items.DeathReportAction``
* ``edc_adverse_event.action_items.DeathReportTmgAction``
* ``edc_adverse_event.action_items.DeathReportTmgSecondAction``
* ``edc_adverse_event.model_mixins.DeathReportTmgModelMixin``
* ``edc_adverse_event.model_mixins.DeathReportTmgSecondModelMixin``

Relevant constants
++++++++++++++++++

* ``DEATH_REPORT_ACTION``
* ``DEATH_REPORT_TMG_ACTION``
* ``DEATH_REPORT_TMG_SECOND_ACTION``
