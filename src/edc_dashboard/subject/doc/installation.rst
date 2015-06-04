Installation
============

Checkout the latest version of :mod:`lab_requisition` into your project folder::

    svn co http://192.168.1.50/svn/bhp_dashboard_registered_subject


Add :mod:`bhp_dashboard_registered_subject` to your project ''settings'' file::

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
        'bhp_dashboard_registered_subject',
        ...
        'mpepu',
        'mpepu_infant',
        'mpepu_maternal',
        'mpepu_lab',
        ...
        )
      
      
Create a new *dashboard* app within your project. For example if your local apps 
are prefixed with *mpepu* create *mpepu_dashboard*.