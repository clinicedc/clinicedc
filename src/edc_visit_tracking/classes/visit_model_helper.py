from django.db.models import ForeignKey, OneToOneField
from django.db.models import get_app, get_models
from ..models import BaseVisitTracking
from ..exceptions import VisitTrackingError


class VisitModelHelper(object):

    """ Help determine the name of the visit model foreign key and to return a queryset of that
    field for select/dropdowns (e.g. formfield_for_foreignkey in admin).

    I separated this code from BaseVisitModelAdmin because other models may wish to use it in their ModelAdmin
    which may not inheret from BaseVisitModelAdmin. For example, the lab requisition has a visit model
    foreign key, needs to determine the visit field and get a queryset for the select/dropdown but its
    ModelAdmin class does not inheret from BaseVisitModelAdmin.
    """
    @classmethod
    def get_field_name(self, cls):
        """Given a class, returns the field attname that is a subclass of BaseVisitTracking."""
        #lst = [f.to for f in [field.rel for field in cls._meta.fields if field.rel] if issubclass(f.to, BaseVisitTracking)]
        lst = []
        for f in cls._meta.fields:
            if f.rel:
                if issubclass(f.rel.to, BaseVisitTracking):
                    lst.append(f)
        if not lst:
            raise VisitTrackingError('Unable to determine the visit field in class {0}.'.format(cls))
        if not len(lst) == 1:
            raise VisitTrackingError('Found more than one visit field in class {0}.'.format(cls))
        return lst[0].name

    @classmethod
    def get_field_cls(self, cls):
        """Given a class, returns the model class that is a subclass of BaseVisitTracking."""
        lst = [f.to for f in [field.rel for field in cls._meta.fields if field.rel] if issubclass(f.to, BaseVisitTracking)]
        if not lst:
            raise VisitTrackingError('Unable to determine the visit field in class {0}.'.format(cls))
        if not len(lst) == 1:
            raise VisitTrackingError('Found more than one visit field in class {0}.'.format(cls))
        return lst[0]

    def set_visit_queryset(self, **kwargs):
        """Returns a queryset of one visit model for the admin change form dropdown."""
        visit_model = kwargs.get('visit_model')
        subject_identifier = kwargs.get('subject_identifier')
        visit_code = kwargs.get('visit_code')
        visit_instance = kwargs.get('visit_instance')
        pk = kwargs.get('pk')
        if pk:
            return visit_model.objects.filter(pk=pk)
        else:
            return visit_model.objects.filter(
                appointment__registered_subject__subject_identifier=subject_identifier,
                appointment__visit_definition__code=visit_code,
                appointment__visit_instance=visit_instance)

    def get_visit_field(self, **kwargs):
        model = kwargs.get('model')
        visit_model = kwargs.get('visit_model')
        visit_fk = None
        try:
            visit_fk = [fk for fk in [f for f in model._meta.fields if isinstance(f, ForeignKey)] if fk.rel.to._meta.module_name == visit_model._meta.module_name]
        except:
            pass
        if not visit_fk:
            for f in model._meta.fields:
                if isinstance(f, ForeignKey, OneToOneField):
                    cls = f.rel.to
                    if isinstance(visit_model, cls):
                        visit_fk = f
                        break
        return visit_fk[0].name

    def get_visit_model(self, instance):
        """ given the instance (or class) of a model, return the visit model of its app """
        for model in get_models(get_app(instance._meta.app_label)):
            if isinstance(model(), BaseVisitTracking):
                return model
        raise TypeError('Unable to determine the visit model from instance {0} for app {1}'.format(instance._meta.model_name, instance._meta.app_label))

    def get_fieldname_from_cls(self, cls):
        return self.get_visit_field(cls, self.get_visit_model(cls))
