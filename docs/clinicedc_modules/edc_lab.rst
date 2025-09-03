edc-lab
=======

Add to settings:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'edc_lab.apps.AppConfig',
        ...
    ]

Configuration
+++++++++++++

Create aliquot types:

.. code-block:: python

    # aliquot types
    wb = AliquotType(name='whole_blood', alpha_code='WB', numeric_code='02')
    bc = AliquotType(name='buffy_coat', alpha_code='BC', numeric_code='16')
    pl = AliquotType(name='plasma', alpha_code='PL', numeric_code='32')

Add possible derivatives to an aliquot type:

.. code-block:: python

    # in this case, plasma and buffy coat are possible derivatives
    wb.add_derivatives(pl, bc)

Set up a processing profile:

.. code-block:: python

    viral_load = ProcessingProfile(
        name='viral_load', aliquot_type=wb)
    process_bc = Process(aliquot_type=bc, aliquot_count=4)
    process_pl = Process(aliquot_type=pl, aliquot_count=2)
    viral_load.add_processes(process_bc, process_pl)

Create a``panel`` that uses the processing profile:

.. code-block:: python

    panel = RequisitionPanel(
        name='Viral Load',
        processing_profile=viral_load)

Add the panel (and others) to a lab profile:

.. code-block:: python

    lab_profile = LabProfile(
        name='lab_profile',
        requisition_model='edc_lab.subjectrequisition')
    lab_profile.add_panel(panel)

Register the ``lab_profile`` with the site global:

.. code-block:: python

    site_labs.register(lab_profile)

Usage
+++++

Create a requisition model instance:

.. code-block:: python

    requisition = SubjectRequisition.objects.create(
        subject_visit=self.subject_visit,
        panel_name=self.panel.name,
        is_drawn=YES)

Pass the requisition to ``Specimen``

.. code-block:: python

    specimen = Specimen(requisition=requisition)

Process:

.. code-block:: python

    specimen.process()

Aliquots have been created according to the configured processing profile:

.. code-block:: python

    >>> specimen.primary_aliquot.identifier
    '99900GV63F00000201'

    >>> for aliquot in specimen.aliquots.order_by('count'):
           print(aliquot.aliquot_identifier)
    '99900GV63F00000201'
    '99900GV63F02013202'
    '99900GV63F02013203'
    '99900GV63F02011604'
    '99900GV63F02011605'
    '99900GV63F02011606'
    '99900GV63F02011607'
