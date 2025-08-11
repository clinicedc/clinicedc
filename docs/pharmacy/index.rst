.. Pharmacy documentation master file, created by
   sphinx-quickstart on Tue Jul 22 12:26:51 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Pharmacy documentation
======================

`EDC pharmacy <https://clinicedc.readthedocs.io/en/latest/>`_ is a simple pharmacy module for randomized control trials integrated in `Clinic EDC <https://github.com/clinicedc>`_  projects as a `submodule <https://github.com/clinicedc/clinicedc/tree/develop/src/edc_pharmacy>`_.

The module includes stock management to enable a research project team to track chain-of-custody of investigational product from a central site to each research site and finally to each patient.
Stock items are physically labeled using the integrated labelling functionality. Generated labels use a randomly generated stock code and code128 barcodes. Label formats are fully customizable.

When integrated with an `Clinic EDC <https://github.com/clinicedc>`_ project, study site requests for stock can be generated using the subject's randomization assignment, followup schedule, and prescription.


.. toctree::
    :maxdepth: 2
    :caption: Contents:

    getting_started
    orders_to_suppliers
    receive
    repack
    prepare_stock_request
    allocation
    transfer_stock_to_site
    confirm_transferred_stock_at_site
    store_stock_at_site
    dispense
