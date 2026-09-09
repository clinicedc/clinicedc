edc_lab_results_import
======================

Imports lab results from a folder of PDF reports into the ``Result``
model, resolves each result to the subject, timepoint and requisition it
belongs to, and reports what could not be resolved or does not agree
with the CRF it was transcribed onto.

Nothing here writes to a CRF. The result CRF stays the record; these
tools say where the two disagree.


Settings
--------

.. code-block:: python

    # parser callable per laboratory, keyed by laboratory name
    EDC_LAB_RESULTS_PARSERS = {"MNH": "..."}

    # utest id and unit mapping files per laboratory
    EDC_LAB_RESULTS_MAPPING_FILES = {"MNH": "..."}

    # where source PDFs are archived after import
    EDC_LAB_RESULTS_IMPORT_PRIVATE_PATH = "~/edc/source_documents"

    # which requisition panel an analyte panel is drawn under
    EDC_LAB_RESULTS_IMPORT_REQUISITION_PANEL_MAP = {"wbc_diff": "fbc"}

The last one needs explaining. The panel a result is *reported* under is
not always the panel it was *drawn* under. The white cell differentials
are their own analyte panel, but no visit schedule requires a
``wbc_diff`` requisition because they are collected on the FBC
requisition. Without this map, looking a requisition up by the analyte
panel can only fail. It is empty by default and an unlisted panel maps
to itself. ``Result.panel_name`` keeps the analyte panel either way,
which is the truthful description of what was measured.


A first import
--------------

.. code-block:: bash

    manage.py import_results <folder> --laboratory MNH --dry-run
    manage.py import_results <folder> --laboratory MNH

Then check what did not resolve:

.. code-block:: python

    from edc_lab_results_import.dataframes import get_df_orphan_results

    df = get_df_orphan_results()
    df.bucket.value_counts()

On a healthy import:

``panel_unknown``
    Should be 0. Anything here is a utest id that is in no registered
    panel, so the result can never be matched to a requisition. Fix the
    mapping before going further. See ``get_mappings``.

``resolver_miss``
    Should be 0 or near it. A requisition already exists for this
    result and the importer did not find it, which means the importer
    missed something rather than the data being wrong. Investigate
    before linking it away.

``requisition_not_keyed``
    The genuine data manager worklist: the panel was expected at this
    timepoint and nobody keyed the requisition.

``visit_not_found``
    No timepoint. Check ``candidate_rule`` for the ones the baseline
    rule can place.

``panel_not_expected``
    A real panel at a timepoint that did not call for it. An ad hoc
    draw, or a mapping worth re-examining.

A data manager keys a requisition, not an analyte, so group by subject,
timepoint and panel for the size of the actual work:

.. code-block:: python

    df.groupby(
        ["subject_identifier", "visit_code", "visit_code_sequence", "panel_name"]
    ).ngroups

Then compare the imported values against the CRFs they were transcribed
onto, which is the point of all of it:

.. code-block:: python

    from edc_lab_results_import.dataframes import get_df_result_comparison

    df = get_df_result_comparison()
    df[df.value_status == "differs"].sort_values("pct_diff", ascending=False)
    df[df.ratio.between(9.5, 10.5)]                            # decimal point slips
    df[(df.n_imported_for_key == 0) & df.crf_value.notna()]    # keyed, nothing imported
    df[df.n_imported_for_key > 1]                              # corrected reports


Repairing a database imported before these fixes
------------------------------------------------

Results imported before ``panel_name`` was persisted carry an empty
panel, so every join keyed on panel is dead: the requisition lookup, the
requisition metadata lookup, and the related visit fallback in
``get_df_result_comparison``.

**Re-importing does not repair them.** ``save_to_model`` skips a row
whose unique key already exists and never updates it. The repair path is
the backfill.

.. code-block:: bash

    manage.py backfill_panel_name --dry-run
    manage.py backfill_panel_name

Set ``EDC_LAB_RESULTS_IMPORT_REQUISITION_PANEL_MAP``, then re-read the
report. The backfill writes the analyte panel and does not consult the
map, so the two can be done in either order, but the map must be set
before the report or the linker mean anything.

.. code-block:: bash

    manage.py link_orphan_results --dry-run
    manage.py link_orphan_results

``link_orphan_results`` consumes the ``resolver_miss`` bucket only:
results carrying no requisition where one is already keyed at their
timepoint for their panel. ``RequisitionModelMixin.Meta`` constrains
panel and related visit to be unique together, so the target is
determined rather than guessed, and no date is matched on. It reads the
report itself rather than an exported worklist, so it cannot act on a
stale one, and it re-reads each result before writing so one linked in
the meantime is left alone.

Both commands save one row at a time so ``simple_history`` records every
change and a run stays reversible from the audit trail. Both are
resumable: an interrupted run picks up where it stopped.


What the repair does not fix
----------------------------

Two things stay as they are for rows imported before these changes.

**Results with no timepoint.** The baseline pass in
``ResultImporter.match_baseline_visits`` runs at import time only. A
specimen collected on or before a subject's first visit cannot belong to
a later timepoint, so baseline is the only candidate, bounded by
``MAX_DAYS_BEFORE_BASELINE``. Existing rows keep their empty
``subject_visit``. ``get_df_orphan_results`` proposes one in
``candidate_subject_visit_id`` and ``candidate_rule``, and names the
requisition waiting there in ``candidate_requisition_id``, but nothing
writes it. A writer would follow the shape of ``ResultLinker``.

**Converted values.** ``converted_result_value`` and
``converted_units`` are declared on the model and read back by
``model_to_dataframe``, but nothing computes them:
``apply_unit_mapping_after_resolve`` only rewrites ``units`` in place.
So the units fallback in the comparison rule never fires, and a result
whose units differ from the CRF reads ``not_compared`` rather than being
converted and compared.


Knowing when a frame has gone stale
-----------------------------------

The frames are queries, not tables, so calling one again always reflects
the database. What goes stale is a dataframe held in a notebook or a
spreadsheet someone exported days ago. ``result_expected`` in particular
is a user driven change, so a worklist pulled before a site edited its
requisitions will overstate the work.

.. code-block:: python

    from edc_lab_results_import.dataframes import changed_since_pulled

    df = get_df_orphan_results()
    changed_since_pulled(df)

Any non-zero count means read it again. Note that ``DataFrame.attrs``
survives a notebook but not a round trip through CSV, so an exported
worklist loses its timestamp.


The comparison rule
-------------------

``comparison_rules.add_comparison_columns`` is the single implementation
of whether an imported result agrees with the CRF. ``ResultComparison``
applies it to the rows behind one CRF on the result search page, and
``get_df_result_comparison`` applies it to every result CRF in the
trial, so the page and the dataframe cannot disagree about the same row.

Value, units and the abnormal flag are compared separately, so a row
that agrees on the value but not the units still reads as a difference.
Differences are taken at the precision the CRF stores, so a value
differing only in decimal places the CRF does not hold reads as exactly
0.0 and sorts to the bottom.
