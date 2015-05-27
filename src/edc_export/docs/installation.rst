Installation
============


Add :mod:`edc.export` and 'edc.notification' to your project ''settings'' file::

    INSTALLED_APPS = (
        ...
        'edc.export',
        'edc.notification',
        ...
        )

run syncdb

if you are using edc.apps.app_configuration you should add the 'export plans' and 'notification plans' to your configuration.


