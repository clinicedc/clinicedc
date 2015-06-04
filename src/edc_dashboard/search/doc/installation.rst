Installation
============

Checkout the latest version of :mod:`bhp_search` into your test environment project folder::

    svn co http://192.168.1.50/svn/bhp_search

Add :mod:`bhp_device` to your project ''settings'' file::

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
        'bhp_search',
        ...
        )
        
Add to the main EDC study-specific app's :file:`urls.py`::

    from mpepu.classes import SearchByWord, SearchByDate, SearchByWeek
    
    section_names = ('mother','appointment','maternal',
                     'randomize','infant','statistics',
                     'administration')
    urlpatterns = SearchByWord.urlpatterns(section_names)
    urlpatterns += SearchByDate.urlpatterns(section_names)
    urlpatterns += SearchByWeek.urlpatterns(section_names)        
        
        
To the main EDC study-specific app's templates ensure any urls pointing to search
use the same search names. For example if you are searching on `maternalconsent` and `birth`
as declared in :class:`SearchByWord`, the url fragments might be something like this:: 

    "/{section_name}/search/{search_name}"
    "/mother/search/maternalconsent" 
    "/infant/search/birth" 

where `maternalconsent`, `birth` are the search_names.    

Create a template for the results of each search model. Name format is  "{search_name}_include.html". For example, 
if the search model is :class:`Birth`, the search_name is `birth` and the template to display the results is
`birth_include.html`.