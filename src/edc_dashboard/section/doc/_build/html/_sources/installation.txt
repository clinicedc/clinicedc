Installation
============

Checkout the latest version of :mod:`bhp_section` into your test environment project folder::

    svn co http://192.168.1.50/svn/bhp_section

Add :mod:`bhp_section` to your project ''settings'' file::

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.admin',
        'django.contrib.admindocs',
        'django_extensions',
        'audit_trail',
        'bhp_base_model',
        'bhp_common',
        'bhp_section',
        ...
        )
