edc-auth
========

Authentication and permissions for the Edc

Default Groups
++++++++++++++


The default groups are required for the normal operation of an EDC deployment. The default groups are:

* ``ACCOUNT_MANAGER``: members may add/change and delete user accounts
* ``ADMINISTRATION``: members may view the Administration page
* ``AUDITOR``: members may view all forms but have no add/change permissions.
* ``CLINIC``: members may add/edit/delete all CRFs, Requisitions, Actions and other required clinic trial data entry forms. They may also view the Requisition page of the Lab section;
* ``EVERYONE``: members may access the EDC;
* ``LAB``: members may perform all functions in the Lab section (Edit requisitions, receive, process, pack, manage manifests, etc);
* ``PHARMACY``:
* ``PII``: members may view all personally identifiable data and edit forms that manage such data (Screening, Consents, Patient registration);
* ``PII_VIEW``: members may view personally identifiable data but have no add/edit permissions for any of the forms that store such data.

Permissions
+++++++++++

Permissions use Django's permission framework,  therefore, all permissions are linked to some model.

Permissions don't always naturally link to a model. In such cases, a dummy model is created.
For example, with Navigation bars from `edc_navbar`. Permissions to follow an item on a
navigation bar are associated with model `edc_navbar.Navbar`. A similar approach is used for
`listboard` permissions using `edc_dashboard.Dashboard`.

Extending permissions with `site_auths` global
++++++++++++++++++++++++++++++++++++++++++++++

A module can add new or update existing groups and roles and even add custom codenames.

The ``site_auths`` global ``autodiscovers`` configurations from ``auths.py`` in the root of your module.
The ``site_auths`` global gathers but does not validate or change any data in django's
``group``/``permission`` models or the Edc's ``role`` model.

The ``site_auths`` global gathers data:
* to ADD new groups,
* to update codenames for an existing group,
* to add a new role
* to update the group list for an existing role
* to add to the list of PII models
* to specifiy custom functions to run before and after groups and roles have been updated

For example,

.. code-block:: python

    # auths.py
    from edc_auth.constants import CLINICIAN_ROLE, STATISTICIAN_ROLE
    from edc_auth.site_auths import site_auths

    from edc_protocol_violation.auth_objects import (
        PROTOCOL_VIOLATION,
        PROTOCOL_VIOLATION_VIEW,
        protocol_violation_codenames,
        protocol_violation_view_codenames,
    )

    # add a new group specific to models in this module
    site_auths.add_group(*protocol_violation_codenames, name=PROTOCOL_VIOLATION)
    # add a new group specific to models in this module
    site_auths.add_group(*protocol_violation_view_codenames, name=PROTOCOL_VIOLATION_VIEW)
    # update the existing role CLINICIAN_ROLE to add the group PROTOCOL_VIOLATION
    site_auths.update_role(PROTOCOL_VIOLATION, name=CLINICIAN_ROLE)
    # update the existing role STATISTICIAN_ROLE to add the group PROTOCOL_VIOLATION_VIEW
    site_auths.update_role(PROTOCOL_VIOLATION_VIEW, name=STATISTICIAN_ROLE)


As a convention, we define group names, lists of codenames and custom functions ``auth_objects.py``.

In the above example, the ``auth_objects.py`` looks like this:

.. code-block:: python

    # auth_objects.py

    # declare group names
    PROTOCOL_VIOLATION = "PROTOCOL_VIOLATION"
    PROTOCOL_VIOLATION_VIEW = "PROTOCOL_VIOLATION_VIEW"
    # add/change/delete/view codenames
    protocol_violation_codenames = (
        "edc_protocol_violation.add_protocoldeviationviolation",
        "edc_protocol_violation.change_protocoldeviationviolation",
        "edc_protocol_violation.delete_protocoldeviationviolation",
        "edc_protocol_violation.view_protocoldeviationviolation",
    )
    # view only codename
    protocol_violation_view_codenames = (
        "edc_protocol_violation.view_protocoldeviationviolation",
    )


AuthUpdater
+++++++++++
The ``AuthUpdater`` class runs in a post_migrate signal declared in ``apps.py``.
The ``AuthUpdater`` reads and validates the data gathered by ``site_auths``. Once all
validation checks pass, the ``AuthUpdater`` updates Django's ``group`` and ``permission``
models as well as the Edc's ``Role`` model.

Validation checks include confirming models refered to in codenames exist. This means that
the app where models are declared must be in your ``INSTALLED_APPS``.

During tests having all codenames load may not be ideal. See below on some strategies for testing.


Testing SiteAuths, AuthUpdater
++++++++++++++++++++++++++++++

An app sets up its own groups and roles using the ``site_auths`` global in ``auths.py``. To test just your apps
configuration, you can prevent ``site_auths`` from autodiscovering other modules by setting::

    EDC_AUTH_SKIP_SITE_AUTHS=True

You can prevent the ``AuthUpdater`` from updating groups and permissions by setting::

    EDC_AUTH_SKIP_AUTH_UPDATER=True

You can then override these attributes in your tests

.. code-block:: python

    @override_settings(
        EDC_AUTH_SKIP_SITE_AUTHS=True,
        EDC_AUTH_SKIP_AUTH_UPDATER=False
    )
    class TestMyTests(TestCase):
        ...


Above the ``site_auths`` global ``autodiscover`` is still disabled but the ``AuthUpdater`` is not.
In your test setup you can update ``site_auths`` manually so that your tests focus on the
add/update or groups/roles/codenames/tuples relevant to your app.

You can emulate ``autodiscover`` behaviour by explicitly importing ``auths`` modules needed for your tests.

For example:

.. code-block:: python

    from importlib import import_module

    from django.test import TestCase, override_settings
    from edc_auth.auth_updater import AuthUpdater


    class TestAuths(TestCase):
        @override_settings(
            EDC_AUTH_SKIP_SITE_AUTHS=True,
            EDC_AUTH_SKIP_AUTH_UPDATER=True,
        )
        def test_load(self):
            import_module(f"edc_dashboard.auths")
            import_module(f"edc_navbar.auths")
            AuthUpdater(verbose=True)


You can ``clear`` the ``site_auths`` registry and add back specific items need for your tests.

For example:

.. code-block:: python

    # taken from edc-dashboard
    @override_settings(EDC_AUTH_SKIP_SITE_AUTHS=True, EDC_AUTH_SKIP_AUTH_UPDATER=False)
    class TestMyTests(TestCase):
        def setUpTestData(cls):
            site_auths.clear()
            site_auths.add_group("edc_dashboard.view_my_listboard", name=CLINIC)
            site_auths.add_custom_permissions_tuples(
                model="edc_dashboard.edcpermissions",
                codename_tuples=(("edc_dashboard.view_my_listboard", "View my listboard"),),
            )
            AuthUpdater(verbose=False, warn_only=True)
            return super().setUpTestData()

        def test_me(self):
            ...



Importing users
+++++++++++++++

You create user accounts by importing a specially formatted CSV file. Once an account is created a "Welcome" email may be sent.

Import users from a CSV file with columns:

.. code-block:: bash

    username
    is_staff
    is_active
    first_name
    last_name
    job_title
    email
    mobile
    alternate_email
    site_names: a comma-separated list of sites
    role_names: a comma-separated list of roles


Then import the users from your application commandline

.. code-block:: bash

    python manage.py import_users --csvfile=/Users/erikvw/meta_users.csv --notify-to-test-email=ew2789@gmail --resource-name=meta.clinicedc.org --resend-as-new

Legacy notes
++++++++++++

**Important:** If you are upgrading from edc_base.auth:

The ``userprofile`` table is now in ``edc_auth``. ``edc_auth`` has one migration for this table.
Copy the same table from ``edc_base`` and fake the ``edc_auth`` migration.

.. code-block:: sql

    CREATE TABLE edc_auth_userprofile LIKE edc_base_userprofile;

    INSERT edc_auth_userprofile SELECT * FROM edc_base_userprofile;


.. code-block:: bash

    python manage.py migrate edc_auth --fake

You can now run the ``edc_base`` migration safely.
