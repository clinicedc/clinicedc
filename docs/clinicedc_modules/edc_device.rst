edc-device
==========

``edc-device`` provides device roles unique device IDs for hosts and clients where the hostname may not be reliable. Hosts can be group as servers, clients, node_servers and some of their functionality limited according to this role.

A unique device ID is used to seed unique subject and sample identifiers. Uniqueness is evaluated during deployment.

Device information is set in and read from ``edc_device.apps.AppConfig``.

You should subclass into your projects ``apps.py`` like this, for example:

.. code-block:: python

    from edc_device.apps import AppConfig as EdcDeviceAppConfigParent

    class EdcDeviceAppConfig(EdcDeviceAppConfigParent):
        device_id = '32'
        device_role = CLIENT
        device_permissions = DevicePermissions(
            plot_add, plot_change,
            #...
            )

and then in your settings:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        my_app.apps.EdcDeviceAppConfig,
        myapp.apps.AppConfig,
    ]

Include in your ``urls.py``:

.. code-block:: python

    urlpatterns = [
        # ...
        path('edc_device/', include('edc_device.urls')),
        # ...
    ]

To get to the Edc Device home page, reverse the url like this:

.. code-block:: python

    reverse('edc_device:home_url')


Usage
-----


A ``client`` might look like this:

.. code-block:: python

    class EdcDeviceAppConfig(EdcDeviceAppConfigParent):
        device_id = '18'
        node_server_id_list = [97, 98, 99]
        middleman_id_list = [95, 96]

and ::

    >>> from django.apps import apps as django_apps
    >>> app_config = django_apps.get_app_config('edc_device')
    >>> app_config.device_id
    '18'
    >>> app_config.is_client
    True
    >>> app_config.device_role
    'Client'

A node server server might look like this:

.. code-block:: python

    class EdcDeviceAppConfig(EdcDeviceAppConfigParent):
        device_id = '98'
        node_server_id_list = [97, 98, 99]
        middleman_id_list = [95, 96]

and ::

    >>> from django.apps import apps as django_apps
    >>> app_config = django_apps.get_app_config('edc_device')
    >>> app_config.device_id
    '98'
    >>> app_config.is_node_server
    True
    >>> app_config.device_role
    'NodeServer'

A middleman server might look like this:

.. code-block:: python

    class EdcDeviceAppConfig(EdcDeviceAppConfigParent):
        device_id = '95'
        node_server_id_list = [97, 98, 99]
        middleman_id_list = [95, 96]

and ::

    >>> from django.apps import apps as django_apps
    >>> app_config = django_apps.get_app_config('edc_device')
    >>> app_config.device_id
    '95'
    >>> app_config.is_middleman
    True
    >>> app_config.device_role
    'Middleman'

The central server might look like this:

.. code-block:: python

    class EdcDeviceAppConfig(EdcDeviceAppConfigParent):
        device_id = '99'
        node_server_id_list = [97, 98, 99]
        middleman_id_list = [95, 96]

and ::

    >>> from django.apps import apps as django_apps
    >>> app_config = django_apps.get_app_config('edc_device')
    >>> app_config.device_id
    '99'
    >>> app_config.is_middleman
    True
    >>> app_config.device_role
    'CentralServer'


See also ``django-collect-offline``.


Device Permissions by Model
---------------------------

You can use the device role, or the device ID, to limit ADD/CHANGE permissions on a model.

``edc-device`` AppConfig maintains a collection of ``DeviceAddPermission`` and ``DeviceChangePermission`` instances that are inspected in the ``save`` method of a model using the ``DeviceModelMixin``.

To declare a ``DeviceAddPermission`` object:

.. code-block:: python

    test_model_add = DeviceAddPermission(
        model='my_app.mymodel', device_roles=[NODE_SERVER, CENTRAL_SERVER])

To declare a ``DeviceChangePermission`` object:

.. code-block:: python

    test_model_change = DeviceChangePermission(
        model='my_app.mymodel', device_roles=[CLIENT])

This means that if ``app_config.device_role`` is anything other than ``NODE_SERVER`` or ``CENTRAL_SERVER``, the save method will raise a ``DevicePermissionsAddError``.

To register the instances with ``edc_device.apps.AppConfig.device_permissions``:

.. code-block:: python

    device_permissions = DevicePermissions(test_model_add, test_model_change)

This means that if ``app_config.device_role`` is anything other than ``CLIENT``, the save method will raise a ``DevicePermissionsChangeError``.

On boot up you should see::

    Loading Edc Device ...
      * device id is '10'.
      * device role is 'Client'.
      * device permissions exist for:
        - edc_device.testmodel ADD NodeServer,CentralServer
        - edc_device.testmodel CHANGE Client
    Done loading Edc Device.

Models declared with the ``EdcDeviceModelMixin`` check the device permissions collection on save. Note the model mixin is already declared with ``BaseUuidModel``.

.. code-block:: python

    from edc_model.models import BaseUuidModel

    class TestModel(BaseUuidModel):
        pass


Declaring device permissions directly on model ``Meta`` class:
--------------------------------------------------------------

You can declare device permissions on ``Meta.device_permissions`` in the same way as above.

.. code-block:: python

    [...]
    class Meta(DeviceModelMixin.Meta):
        device_permissions = DevicePermissions(...)

Both ``Meta`` and ``AppConfig`` device permissions will be called, where the ``Meta`` class object will be called first.

Disable device permissions by model instance:
---------------------------------------------

You can disable device permissions ``per model instance`` by setting ``check_device_permissions`` to ``False``


Customizing Device Permissions
------------------------------

The ADD and CHANGE device permission objects by default inspect the model's ``id``. If ``obj.id`` is ``None``, it as an ADD model operation; If ``obj.id`` is not ``None``, it is a CHANGE model operation.

You can change this by overriding the ``model_operation`` method. The ``model_operation`` must return ``None`` or some value, such as ``self.label``.

For example:

.. code-block:: python

    # default for DeviceAddPermission
    label = 'ADD'

    def model_operation(self, model_obj=None, **kwargs):
        if not model_obj.id:
            return self.label
        return None

    # overridden
    def model_operation(self, model_obj=None, **kwargs):
        """Return ADD if both id and plot identifier are None.
        """
        if not model_obj.id and not obj.plot_identifier:
            return self.label
        return None
