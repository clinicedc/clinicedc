Stock take
==========

A *stock take* is a physical inventory count of a single storage bin. You scan the
stock codes of the items physically present in the bin, and the EDC compares the scanned
codes against the items it *expects* to find in that bin (the ``StorageBinItem`` records).
The result is recorded as a permanent reconciliation report.

A stock take answers one question for each bin: *does what is physically in the bin match
what the EDC says should be in the bin?* Each scanned/expected code is classified as:

* **matched** — expected (registered in the bin) **and** scanned;
* **missing** — expected, but **not** scanned (a discrepancy);
* **unexpected** — scanned, but **not** registered in this bin (a discrepancy). If the scanned
  code is not found anywhere in the system, it is still recorded, with no linked stock.

.. note::

   A stock take is an audit *snapshot*. Submitting a stock take does **not** move stock or
   change the contents of the bin. It records what was found so that discrepancies can be
   investigated and resolved through the normal stock workflows.


Start a stock take
------------------

From the central or site pharmacy home page, select **Stock take**. This opens the stock
take landing page listing every bin currently in use, together with its current item count
and a summary of its most recent stock take.

Find the bin you want to count and click **Start stock take**. This opens the scan page for
that bin, showing the number of items registered in the bin and a reference list of the
expected stock codes.


Scan the bin
------------

With the cursor in the **Scan stock code** field, scan (or type) the code on each physical
item in the bin and press Enter, or click **Add**. As you scan:

* codes are upper-cased and duplicates are ignored automatically;
* each scanned code appears as a removable badge, and a running *codes scanned* counter is
  shown next to the *expected* count;
* if a scanned code is in the expected list, its row is highlighted.

If you scan something in error, click the ``×`` on its badge to remove it. When every item
physically present in the bin has been scanned, click **Submit**.


Review the results
------------------

On submit, the EDC compares the scanned codes against the expected codes and records the
stock take with its summary counts and one entry per code, classified as *matched*,
*missing*, or *unexpected*. You are then taken to the results page for that stock take,
where the items are grouped by outcome.

Completed stock takes can also be reviewed from the admin under **Pharmacy: Stock Takes**,
where each record shows its counts and an inline list of items, plus a link to the results
page. Stock take records are read-only apart from the free-text **note** field.


Discrepancy report
------------------

From the stock take landing page, select **Discrepancy report** to see, grouped by location,
only those bins whose **most recent** stock take has missing or unexpected items. Bins whose
latest count matched exactly are omitted. A printable PDF version of the report is available
from the same page.

Use this report to drive follow-up: locate missing items, return unexpected items to their
correct bin, and re-run the stock take once the bin has been corrected.


Resolving discrepancies
-----------------------

A stock take *reports* discrepancies; you resolve them from the discrepancy report (or the
results page), and every correction is written to the stock ledger so the chain of custody is
preserved. Each resolved item is linked to the transaction that resolved it and is marked
**Resolved** in place.

Start by investigating each flagged code. On the discrepancy report, every missing or
unexpected code links to that item's **ledger** (transaction history), which shows where the
item has been and what last happened to it. A code marked *(not in system)* was scanned but
is not known to the EDC at all — most often a mislabelled or foreign label that needs to be
investigated by hand and cannot be resolved from the report.

The report also cross-checks each code against the other bins and shows a hint where
relevant. In particular, a **missing** item whose code was *also scanned as unexpected in
another bin* is flagged with a warning — it is most likely misfiled there, **not** lost, so
resolve it from that bin rather than marking it lost here. A quieter note shows when a code is
currently registered in a different bin than the one it appears in.

Each open discrepancy has a **Resolve** control in its row.

**Missing** (expected in the bin, but not found):

* A stock take reconciles *location*, so the only outcome a count can conclude is **lost**:
  enter a short reason and click **Mark lost**. (Condition dispositions — damaged, expired,
  voided — are made in the stock-adjustment workflow, where the item is in hand.)
* If the item is **accounted for in another bin** (the row shows *"also scanned as unexpected
  in bin NN"* or *"now registered in bin NN"*), it is not lost, so **Mark lost** is not
  offered. Investigate, then click **Acknowledge** with a note to clear the row.

**Unexpected** (scanned in the bin, but not registered there):

* The item is physically present, so click **Add to bin** to record it as belonging to the
  bin being counted. No reason is asked for — an audit note is recorded automatically. The
  row then shows **Resolved** with an **Undo** button; clicking **Undo** returns the item to
  its original bin and re-opens the discrepancy.
* Because the same item being missing from another bin is the other half of the same problem,
  **Add to bin** also clears any open *missing* record for that code in other bins — both
  sides are resolved by the one move, and a single **Undo** re-opens both.
* If the item does not belong in this bin, move it to its correct bin from that bin's page
  instead.
* Some unexpected items **cannot** be added to a bin — a code *not in the system*, or a stock
  already in a terminal state (e.g. dispensed). These show **Cannot add to bin** with the
  reason, and an **Acknowledge** action: after investigating, record a short note and click
  **Acknowledge** to mark the row reviewed and clear it. **Undo** re-opens it.

Once a missing row is resolved it shows a **Resolved** badge linking to the resolving
transaction. Note that the bin remains on the discrepancy report until you **redo the stock
take** for it,
since the report reflects the counts captured at the time of the take. When the bin's physical
contents and the EDC records agree again, return to the bin on the stock take landing page
(or use **Redo stock take**) and run the count again. A clean count drops the bin from the
discrepancy report.
