edc-identifier
==============

Add research subject identifiers and other useful identifiers to your project

Installation
------------

Add to settings:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'edc_identifier.apps.AppConfig',
        # ...
    ]

Identifiers for research subjects
---------------------------------

Create subject identifiers.

.. doctest:: identifier-example

    >>> from edc_identifier.subject_identifier import SubjectIdentifier
    >>> subject_identifier = SubjectIdentifier(
    ...    subject_type_name='subject',
    ...    model='edc_example.enrollment',
    ...    protocol='000',
    ...    device_id='99',
    ...    study_site='40')
    >>> subject_identifier.identifier
    '000-40990001-6'


Maternal and Infant Identifiers
-------------------------------

See also, ``edc_pregnancy`` model mixins ``DeliveryMixin``, ``BirthMixin``.

For example:

.. doctest:: maternal-identifier

    >>> from edc_identifier.maternal_identifier import MaternalIdentifier
    >>> maternal_identifier = MaternalIdentifier(
    ...    subject_type_name='maternal',
    ...    model='edc_example.enrollment',
    ...    study_site='40',
    ...    last_name='Carter')
    >>> maternal_identifier.identifier
    '000-40990001-6'

Add infants

.. doctest:: maternal-identifier-infants

    >>> maternal_identifier.deliver(2, model='edc_example.maternallabdel')
    >>> [infant.identifier for infant in maternal_identifier.infants]
    ['000-40990001-6-25', '000-40990001-6-26']

``maternal_identifier.infants`` is a list of ``InfantIdentifier`` instances

Reload class:

.. doctest:: maternal-identifier-infants2

    >>> maternal_identifier = MaternalIdentifier(identifier='000-40990001-6')
    >>> maternal_identifier.identifier
    '000-40990001-6'
    >>> [infant.identifier for infant in maternal_identifier.infants]
    ['000-40990001-6-25', '000-40990001-6-26']

Only allocate an identifier to one infant of twins:

.. doctest:: maternal-identifier-infants3

    >>> maternal_identifier.deliver(2, model='edc_example.maternallabdel', birth_orders='2')
    >>> [infant.identifier for infant in maternal_identifier.infants]
    [None, '000-40990001-6-26']

Of triplets, allocate identifiers to the 2nd and 3rd infants only:

.. doctest:: maternal-identifier-infants4

    >>> maternal_identifier.deliver(3, model='edc_example.maternallabdel', birth_orders='2,3')
    >>> [infant.identifier for infant in maternal_identifier.infants]
    [None, '000-40990001-6-37', '000-40990001-6-38']


Research subject identifier classes can create a Registered Subject instance

See also ``edc_registration``

``SubjectIdentifier`` by default does not create a ``RegisteredSubject`` instance unless ``create_registration=True``.

By default, ``MaternalIdentifier`` and ``InfantIdentifier`` create ``RegisteredSubject`` instances that can be updated with full details later with the Delivery and Birth models. Continuing from above:

.. doctest:: maternal-identifier-infants5

    >>> maternal_identifier = MaternalIdentifier(identifier='000-40990001-6')
    >>> maternal_identifier.deliver(1, model='edc_example.maternallabdel', create_registration=True)

    # mother
    >>> RegisteredSubject.objects.get(subject_identifier='000-40990001-6')
    <RegisteredSubject '000-40990001-6'>

    # infant is linked to the mother
    >>> RegisteredSubject.objects.get(linked_identifier='000-40990001-6')
    <RegisteredSubject '000-40990001-6-10'>

    # infant
    >>> obj = RegisteredSubject.objects.get(subject_identifier='000-40990001-6-10')
    >>> obj.first_name
    'Baby1Carter'  # generates a temp name until Birth form is added with complete information.
    >>> obj.relative_identifier
    '000-40990001-6'


Subject type "Caps" are enforced by the research subject identifier classes

See also ``edc_protocol``

Limits on the number of identifiers that can be allocated per subject type are enforced when identifiers are created. ``edc_identifier`` reads the "caps" from ``edc_protocol.apps.AppConfig`` linking the subject type, e.g. ``subject``, or ``maternal`` or ``infant``, to the relevant cap and not allowing the number of allocated identifiers to exceed the cap.

(Subject type "Caps" still working? needs to be verified)

Numeric Identifiers
-------------------

The numeric identifier uses a check-digit and may have a separator if specified.

.. doctest:: numeric-identifier-infants5

    >>> from edc_identifier import NumericIdentifier
    >>> class MyIdentifier(NumericIdentifier):
    ...    pass

    >>> my_id = MyIdentifier(None)
    >>> my_id
    MyIdentifier('00000000018')
    >>> next(my_id)
    '00000000026'
    >>> next(my_id)
    '00000000034'

    # add a separator
    >>> class MyIdentifier(NumericIdentifier):
    ...    identifier_pattern = r'^[0-9]{4}\-[0-9]{4}\-[0-9]{4}$'
    ...    checkdigit_pattern = r'^\-[0-9]{1}$'
    ...    separator = '-'
    ...    seed = ['3200-0000-0000']

    >>> my_id = MyIdentifier(None)
    >>> my_id
    MyIdentifier('3200-0000-0001-1')
    >>> next(my_id)
    '3200-0000-0002-9'
    >>> next(my_id)
    '3200-0000-0003-7'

    # start from the last identifier, increment is immediate and automatic
    >>> my_id = MyIdentifier('3200-0000-3222-0')
    >>> my_id
    MyIdentifier('3200-0000-3223-8')


Alphanumeric Identifiers
------------------------

.. code-block:: python

	from edc_identifier import AlphanumericIdentifier

	class MyIdentifier(AlphanumericIdentifier):
		alpha_pattern = r'^[A-Z]{3}$'
		numeric_pattern = r'^[0-9]{4}$'
		seed = ['AAA', '0000']


.. doctest:: numeric-identifier-infants5

    >>> my_id = MyIdentifier(None)
    >>> my_id
    MyIdentifier('AAA00015')

Your identifier will starts with 'AAA0001' plus the checkdigit "5". Subsequent calls to next increment like this:

.. doctest:: print-next

    >>> print(next(id))
    AAA00023
    >>> print(next(id))
    AAA00031
    >>> print(next(id))
    AAA00049


The identifier increments on the numeric sequence then the alpha:

.. doctest:: identifier-increments

    >>> my_id = MyIdentifier('AAA99991')
    >>> my_id
    MyIdentifier('AAB00013')

    >>> next(my_id)
    'AAB00021'
    >>> next(my_id)
    'AAB00039'
    >>> next(my_id)
    'AAB00047'

    >>> my_id = MyIdentifier('AAB99999')
    >>> my_id
    MyIdentifier('AAC00010')
    # ...

See ``getresults-receive`` for sample usage with ``settings`` and a ``History`` model.

Short Identifiers
-----------------

Creates a small identifier that is almost unique, for example, across 25 Edc devices in a community. We use these as sample requisition identifiers that are transcribed manually onto a tube from the Edc screen in a household. Once the sample is received at the local lab it is allocated a laboratory-wide unique specimen identifier.

.. doctest:: short-identifier

    >>> from edc_identifier import ShortIdentifier
    >>> ShortIdentifier()
    ShortIdentifier('46ZZ2')

Add a static prefix -- ``prefix(2) + identifier(5)``:

.. doctest:: short-identifier2

    >>> from edc_identifier import ShortIdentifier

    >>> class MyIdentifier(ShortIdentifier):
    ...    prefix_pattern = r'^[0-9]{2}$'

    >>> options = {'prefix': 22}
    >>> my_id = MyIdentifier(options=options)
    >>> my_id
    MyIdentifier('22UYMBT')
    >>> next(my_id)
    '22KM84G'

Add a checkdigit -- ``prefix(2) + identifier(5) + checkdigit(1)``:

.. doctest:: identifier-with-checkdigit

    >>> from edc_identifier import ShortIdentifier

    >>> class MyIdentifier(ShortIdentifier):
    ...    prefix_pattern = r'^[0-9]{2}$'
    ...    checkdigit_pattern = r'^[0-9]{1}$'

    >>> options = {'prefix': 22}
    >>> my_id = MyIdentifier(options=options)
    >>> my_id
    MyIdentifier('223GF8A3')
    >>> next(my_id)
    '22DXVW23'

We use this in edc-quota to get a confirmation code:

.. doctest:: identifier-quota

    >>> from edc_identifier import ShortIdentifier

    >>> class ConfirmationCode(ShortIdentifier):
    ...    identifier_type = 'confirmation'
    ...    prefix_pattern = ''

    >>> code = ConfirmationCode()
    >>> print(code)
    CAT33
    >>> next(code)
    3FU7D

Add more to the prefix, such as device code and community code.

.. code-block:: python

    from edc_identifier.short_identifier import ShortIdentifier

    class RequisitionIdentifier(ShortIdentifier):
        identifier_type = 'requisition'
        prefix_pattern = r'^[0-9]{4}$'
        template = '{device_id}{community_id}{random_string}'

        @property
        def options(self):
            if 'prefix' not in self._options:
                self._options.update(
                    {'prefix': str(self._options.get('device_id')) + str(self._options.get('community_id'))})
            return self._options

.. doctest:: requisition-identifier

    >>> options = {'device_id': 22, 'community_id': '12'}
    >>> my_id = RequisitionIdentifier(options=options)
    >>> my_id
    RequisitionIdentifier('22126MZXD')
    >>> next(my_id)
    '2212Y899C'

... if you prefer not to use the ``IdentifierHistory`` model, for example, if you are filling in a model field on ``save()``:

.. code-block:: python

    from my_app.models import Requisition

    class RequisitionIdentifier(ShortIdentifier):
        identifier_type = 'requisition'
        requisition_model = Requisition

        def is_duplicate(self, identifier):
            try:
                self.requisition_model.get(requisition_identifier=identifier)
                return True
            except self.requisition_model.DoesNotExist:
                pass
            return False

        def update_history(self):
            pass


Batch Identifier
----------------

To have an identifier prefixed by the current date stamp:


.. doctest:: batch-identifier

    >>> from edc_identifier.batch_identifier import BatchIdentifier

    >>> datetime.today().strftime('%Y%m%d')
    20150817
    >>> my_id = BatchIdentifier()
    >>> my_id
    BatchIdentifier('201508170001')
    >>> next(my_id)
    '201508170002'
