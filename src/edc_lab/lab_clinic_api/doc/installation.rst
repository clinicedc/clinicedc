Installation
============

Copy your existing project and dataset into your test environment.

Checkout the latest version of :mod:`lab_clinic_api` into your test environment project folder::

    svn co http://192.168.1.50/svn/lab_clinic_api

Add :mod:`lab_clinic_api` to your project ''settings'' file::

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
        'lab_clinic_api',
        ...
        )
      

:mod:`lab_clinic_api` has an lis import class that accesses the remote LIS
database. The default name of this connection is 'lab_api'. Add this to your
settings DATABASES attribute::

    DATABASES = {
        'default': {
            ...
            ...
        },
        'lab_api': {
            'ENGINE': 'django.db.backends.mysql',
            'OPTIONS': {'init_command': 'SET storage_engine=INNODB'},
            'NAME': 'lab',
            'USER': 'root',
            'PASSWORD': 'xxxxxx',
            'HOST': '192.168.1.XX',
            'PORT': '3306',
        }
      
      
