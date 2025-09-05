edc-sites
=========

Site definitions to work with Django's `Sites Framework`__ and django_multisite_.

Define a ``sites.py``. This is usually in a separate project module. For example, for project ``meta`` there is a module ``meta_sites`` that contains a ``sites.py``.

Register your sites in ``sites.py``.

.. code-block:: python

    # sites.py
    from edc_sites.site import sites
    from edc_sites.single_site import SingleSite

    suffix = "example.clinicedc.org"

    sites.register(
        SingleSite(
            10,
            "hindu_mandal",
            title="Hindu Mandal Hospital",
            country="tanzania",
            country_code="tz",
            domain=f"hindu_mandal.tz.{suffix}",
        ),
        SingleSite(
            20,
            "amana",
            title="Amana Hospital",
            country="tanzania",
            country_code="tz",
            domain=f"amana.tz.{suffix}",
        ),
    )


A ``post_migrate`` signal is registered in ``apps.py`` to update the django model ``Site`` and the
EDC model ``SiteProfile`` on the next migration:

.. code-block:: python

    # apps.py

    from edc_sites.add_or_update_django_sites import add_or_update_django_sites

    def post_migrate_update_sites(sender=None, **kwargs):
        sys.stdout.write(style.MIGRATE_HEADING("Updating sites:\n"))
        add_or_update_django_sites(verbose=True)
        sys.stdout.write("Done.\n")
        sys.stdout.flush()



Now in your code you can use the ``sites`` global to inspect the trial sites:

.. code-block:: python

    from edc_sites.site import sites

    In [1]: sites.all()
    Out[1]:
    {10: SingleSite(site_id=10, name='hindu_mandal', domain='hindu_mandal.tz.example.clinicedc.org', country='tanzania', description='Hindu Mandal Hospital'),
     20: SingleSite(site_id=20, name='amana', domain='amana.tz.example.clinicedc.org', country='tanzania', description='Amana Hospital')}

    In [2]: sites.get(10)
    Out[2]: SingleSite(site_id=10, name='hindu_mandal', domain='hindu_mandal.tz.example.clinicedc.org', country='tanzania', description='Hindu Mandal Hospital')

    In [3]: sites.get_by_attr("name", 'hindu_mandal')
    Out[3]: SingleSite(site_id=10, name='hindu_mandal', domain='hindu_mandal.tz.example.clinicedc.org', country='tanzania', description='Hindu Mandal Hospital')

    In [4]: sites.get(10).languages
    Out[4]:
    {'sw': 'Swahili',
     'en-gb': 'British English',
     'en': 'English',
     'mas': 'Maasai',
     'ry': 'Runyakitara',
     'lg': 'Ganda',
     'rny': 'Runyankore'}


Take a look at the ``Sites`` class in edc_sites.site for more available methods.

For another deployment, we have alot of sites spread out over a few countries.

For example:

.. code-block:: python

    from edc_sites.site import sites
    from edc_sites.single_site import SingleSite

    suffix = "inte.clinicedc.org"

    sites.register(
        SingleSite(
            101,
            "hindu_mandal",
            title="Hindu Mandal Hospital",
            country="tanzania",
            country_code="tz",
            domain=f"hindu_mandal.tz.{suffix}",
        ),
        SingleSite(
            102,
            "amana",
            title="Amana Hospital",
            country="tanzania",
            country_code="tz",
            domain=f"amana.tz.{suffix}",
        ),
        SingleSite(
            201,
            "kojja",
            country="uganda",
            country_code="ug",
            domain=f"kojja.ug.{suffix}",
        ),
        SingleSite(
            202,
            "mbarara",
            country="uganda",
            country_code="ug",
            domain=f"mbarara.ug.{suffix}",
        ),
    )

You can use the ``sites`` global to get the trial sites for a country:

.. code-block:: python

    from edc_sites.site import sites

    In [1]: sites.get_by_country("uganda")
    Out[1]:
    {201: SingleSite(site_id=201, name='kojja', domain='kojja.ug.inte.clinicedc.org', country='uganda', description='Kojja'),
     202: SingleSite(site_id=202, name='mbarara', domain='mbarara.ug.inte.clinicedc.org', country='uganda', description='Mbarara')}


In a multisite, multi-country deployment, managing the SITE_ID is complicated. We use django_multisite_ which nicely reads
the SITE_ID from the url. django_multisite will extract `kojja` from https://kojja.ug.example.clinicedc.org to do a model lookup
to get the SITE_ID.

Viewing data from multiple sites using ``view_auditallsites``
-------------------------------------------------------------

The mixins provided by``edc_sites`` limit the EDC to only present data linked to the current site.
To expand access beyond the current site, ``edc_sites`` provides a special permission codename;
``view_auditallsites``. If a user has this permission, they will be shown data from the current
site plus any additional sites granted in their user profile.

The permission codename ``view_auditallsites`` cannot be allocated to a user with add/edit/delete
permissions to ANY model in the system. That is, the permission codename ``view_auditallsites``
is reserved for VIEW ONLY access, e.g the AUDITOR_ROLE. The one exception is for ``edc_auth``
and``auth`` models accessible to users granted ACCOUNT_MANAGER_ROLE permissions.

In your code, you can check if a user has access to more than just the current site using function
``may_view_other_sites``:

.. code-block:: python

    if may_view_other_sites(request):
        queryset = self.appointment_model_cls.objects.all()
    else:
        queryset = self.appointment_model_cls.on_site

To get a list of sites that the user has access to in the current request, use function
``get_view_only_site_ids_for_user``.

.. code-block:: python

    from edc_model_admin.utils import add_to_messages_once

    site_ids = get_view_only_site_ids_for_user(request.user, request.site, request=request)


Default Site and tests
----------------------

Edc sites may be configured to register a default site. This may be useful for testing where
you are not registering any sites manually or through ``autodiscover``.

In ``settings``::

    EDC_SITES_REGISTER_DEFAULT=True


The default site id is 1.

If your tests depend on a test app that has a ``sites.py``, you might need to set the SITE_ID in your tests.

Use the ``override_settings`` decorator on the test class or on a specific test.

For example:

.. code-block:: python

    @override_settings(SITE_ID=20)
    class TestLpFormValidator(TestCase):
        def setUp(self):
            ...

        @override_settings(SITE_ID=40)
        def test_lp_not_done(self):
            ...




.. _django_multisite: https://github.com/ecometrica/django-multisite.git

.. _sites_framework: https://docs.djangoproject.com/en/dev/ref/contrib/sites/
__ sites_framework_
