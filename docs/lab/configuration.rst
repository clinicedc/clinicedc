Configuration
=============

Configuring the system for specimen management
----------------------------------------------

Specimen management starts with a ``lab profile`` The lab profile is a container class for testing panels, aliquot types, and aliquot processing. The lab profile is linked to the specimen requisition submitted at the clinic level for tests such as FBC, LFT, etc. A single requisition is submitted per test panel. A panel has its own processing profile that defines the number, type and volume of primary tubes and the number and type of derivative aliquots to be created from the primary tube(s). For example, a requisition with the viral load panel might start with a 5ml whole blood primary tube and be processed into derivative aliquots; 2 of plasma and 4 of buffy coat.

When a requisition is submitted for the primary specimen, the processing profile for the panel is referenced to generate records for the the aliquots to be created. From the aliquot records, specimen labels are generated and specimen management begins.

To configure the system

* define a requisition model
* create a lab profile and some tesing panels
* add the panels to the lab profile (default panels are in edc_lab_panel)
* register the lab profile with the site global.

Define a Requisition model
++++++++++++++++++++++++++

.. code-block:: python

    from edc_crf.model_mixins import CrfStatusModelMixin
    from edc_lab.model_mixins import RequisitionModelMixin
    from edc_model.models import BaseUuidModel


    class SubjectRequisition(RequisitionModelMixin, CrfStatusModelMixin, BaseUuidModel):
        class Meta(RequisitionModelMixin.Meta, CrfStatusModelMixin.Meta, BaseUuidModel.Meta):
            pass


Creating a lab profile
++++++++++++++++++++++
The first step is to define a lab profile. The lab profile is linked to a single requisition model. The requisition model has a key to the Panel model. The same requisition model is used longitudinally for all requisitions for all panels.

.. code-block:: python

    lab_profile = LabProfile(
        name='lab_profile',
        requisition_model='my_app.subjectrequisition')

Building panels to add to the lab profile
+++++++++++++++++++++++++++++++++++++++++
To build a panel:
* define aliqout types;
* add aliquots to a processing profile;
* add the processing profile a panel

Creating aliquot types
~~~~~~~~~~~~~~~~~~~~~~
Each aliquot listed in a processing profile has enough information to generate a unique aliquot identifier for the type.

.. code-block:: python

    # aliquot types
    wb = AliquotType(name='whole_blood', alpha_code='WB', numeric_code='02')
    bc = AliquotType(name='buffy_coat', alpha_code='BC', numeric_code='16')
    pl = AliquotType(name='plasma', alpha_code='PL', numeric_code='32')

Add possible derivatives to an aliquot type:

.. code-block:: python

    # in this case, plasma and buffy coat are possible derivatives
    wb.add_derivatives(pl, bc)


Set up a processing profile
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    viral_load = ProcessingProfile(
        name='viral_load', aliquot_type=wb)
    process_bc = Process(aliquot_type=bc, aliquot_count=4)
    process_pl = Process(aliquot_type=pl, aliquot_count=2)
    viral_load.add_processes(process_bc, process_pl)

Create a tesing panel that uses the processing profile
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    panel = RequisitionPanel(
        name='Viral Load',
        processing_profile=viral_load)

Adding panels to the lab profile
++++++++++++++++++++++++++++++++

Add the panel (and others) to the lab profile:

.. code-block:: python

    lab_profile.add_panel(panel)

Register the lab profile with the site global
+++++++++++++++++++++++++++++++++++++++++++++

.. code-block:: python

    site_labs.register(lab_profile)

