Overview
========   

Module :mod:`lab_clinic_api` adds laboratory data to the Edc. 

    1. The basic data model of follows data through this path: receive->aliquot->order->result-resultitems (ROARR) 
    2. Refers to :mod:`bhp_registration' model :class:`RegisteredSubject` for patient identification and demographics.
    3. :class:`ResultItem` uses :mod:`lab_clinic_reference` for grading and reference range tables and calculations.
 