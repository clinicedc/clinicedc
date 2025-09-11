Usage
=====

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
