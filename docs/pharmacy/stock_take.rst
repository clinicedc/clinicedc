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
