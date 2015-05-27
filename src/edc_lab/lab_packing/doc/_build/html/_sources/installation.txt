Installation
============

Note: :mod:`lab_packing` also requires :mod:`lab_requisition`.

Checkout the latest version of :mod:`lab_packing` into your project folder::

    svn co http://192.168.1.50/svn/lab_packing


Add :mod:`lab_requisition` to your project ''settings'' file::

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
        'lab_requisition',
        'lab_packing',
        ...
        'mpepu',
        'mpepu_infant',
        'mpepu_maternal',
        'mpepu_lab',
        ...
        )
      
      
Create a new *lab* app within your project. For example if your local apps 
are prefixed with *mpepu* create *mpepu_lab*.

Models
------

Two models are required::

    from lab_packing.models import BasePackingList
    
    class PackingList(BasePackingList):
        
        class Meta:
            app_label = "mpepu_lab"
            verbose_name = 'Packing List'  
    
        from django.db import models
        from lab_packing.models import BasePackingListItem
        from packing_list import PackingList

and::    
    
    class PackingListItem(BasePackingListItem):
        
        packing_list = models.ForeignKey(PackingList)
        
        
        class Meta:
            app_label = "mpepu_lab"
            verbose_name = 'Packing List Item'    


ModelForms
----------
Create a form for each packing model::

    # PackingList
    class PackingListForm (BasePackingListForm): 
    
        def clean(self):
    
            self.requisition=[InfantRequisition, MaternalRequisition,]    
            return  super(PackingListForm, self).clean()
    
        class Meta:
            model = PackingList 
          
       
    # PackingList
    class PackingListItemForm (BasePackingListItemForm): 
    
        def clean(self):
    
            self.requisition=[InfantRequisition, MaternalRequisition,] 
            return  super(BasePackingListItemForm, self).clean()
    
        class Meta:
            model = PackingListItem

ModelAdmin
------------------------------------

Then add the ModelAdmin classes to the admin.py to include a reference to the form and 
requisitions for each subject type::

    class PackingListAdmin(BasePackingListAdmin): 
    
        form = PackingListForm
        requisition = [InfantRequisition, MaternalRequisition,]
        packing_list_item_model = PackingListItem
    
    admin.site.register(PackingList, PackingListAdmin)
    
    
    class PackingListItemAdmin(BasePackingListItemAdmin): 
        
        form = PackingListItemForm
        requisition = [InfantRequisition, MaternalRequisition,]
    
    admin.site.register(PackingListItem, BasePackingListItemAdmin)      
