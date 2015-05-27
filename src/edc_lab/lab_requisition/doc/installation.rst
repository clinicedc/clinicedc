Installation
============

Note: :mod:`lab_requisition` also requires :mod:`lab_packing`.

Checkout the latest version of :mod:`lab_requisition` into your project folder::

    svn co http://192.168.1.50/svn/lab_requisition


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

Under *models* create a requisition for each subject type. :mod:`lab_requisition` just
needs a foreignkey to the visit model of each subject type.

For subject type *maternal*::

    from django.db import models
    from audit_trail.audit import AuditTrail
    from lab_requisition.models import BaseClinicRequisition
    from mpepu_maternal.models import MaternalVisit
    
    
    class MaternalRequisition(BaseClinicRequisition):
        
        maternal_visit = models.ForeignKey(MaternalVisit)
        
        history = AuditTrail()
    
        class Meta:
            app_label = 'mpepu_lab'
            verbose_name = 'Maternal Laboratory Requisition'   

...and for subject type *infant*::

    from django.db import models
    from audit_trail.audit import AuditTrail
    from lab_requisition.models import BaseClinicRequisition
    from mpepu_infant.models import InfantVisit


    class InfantRequisition(BaseClinicRequisition):
        
        infant_visit = models.ForeignKey(InfantVisit)
        
        history = AuditTrail()
    
        class Meta:
            app_label = 'mpepu_lab'
            verbose_name = 'Infant Laboratory Requisition'


        

ModelForms
----------
Create a form for each requisition model::

    # InfantRequisition
    class InfantRequisitionForm (BaseRequisitionForm): 
        
        def clean(self):
            #cleaned_data = self.cleaned_data 
            return super(InfantRequisitionForm, self).clean()
            
        class Meta:
            model = InfantRequisition
    
    # MaternalRequisition
    class MaternalRequisitionForm (BaseRequisitionForm): 
        
        def clean(self):
            #cleaned_data = self.cleaned_data 
            return super(MaternalRequisitionForm, self).clean()
            
        class Meta:
            model = MaternalRequisition


ModelAdmin Classes for Subject Types
------------------------------------

Under *classes* add a model admin class for each requisition model. Lab requisitions have a key to the subject's visit
model and appear on the subject's dashboard.::

    from lab_requisition.classes import BaseRequisitionModelAdmin
    from mpepu_infant.models import InfantVisit
    
    
    class InfantRequisitionModelAdmin (BaseRequisitionModelAdmin):
    
        visit_model = InfantVisit
        visit_fieldname = 'infant_visit'
        dashboard_type = 'infant'   
        
and::

    from lab_requisition.classes import BaseRequisitionModelAdmin
    from mpepu_maternal.models import MaternalVisit
    
    
    class MaternalRequisitionModelAdmin (BaseRequisitionModelAdmin):
    
        visit_model = MaternalVisit
        visit_fieldname = 'maternal_visit'
        dashboard_type = 'maternal'    


Then add the ModelAdmin classes to the admin.py including a reference to the form::

    # MaternalRequisition
    class MaternalRequisitionAdmin(MaternalRequisitionModelAdmin): 
        form = MaternalRequisitionForm
    admin.site.register(MaternalRequisition, MaternalRequisitionAdmin)
    
    
    # InfantRequisition
    class InfantRequisitionAdmin(InfantRequisitionModelAdmin): 
        form = InfantRequisitionForm
    admin.site.register(InfantRequisition, InfantRequisitionAdmin)        
        
