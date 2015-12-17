from django import template
from django.core.urlresolvers import reverse

from edc_visit_tracking.classes import VisitModelHelper

register = template.Library()


def render_appointment_row(context, appointment):

    """Given an apointment instance, render to template
    an appointment/visit report row for the clinic dashboard."""

    my_context = {}
    my_context['appointment'] = appointment
    my_context['subject_dashboard_url'] = context['subject_dashboard_url']
    my_context['subject_dashboard_visit_url'] = context['subject_dashboard_visit_url']
    my_context['appointment_meta'] = context['appointment_meta']
    my_context['visit_model_instance'] = None
    my_context['visit_code'] = context['visit_code']
    my_context['visit_instance'] = context['visit_instance']
    my_context['appointment_visit_report'] = False
    my_context['dashboard_type'] = context['dashboard_type']
    my_context['subject_identifier'] = context['subject_identifier']
    my_context['registered_subject'] = context['registered_subject']
    my_context['app_label'] = context['app_label']
    my_context['visit_model'] = context['visit_model']
    my_context['visit_model_meta'] = context['visit_model_meta']
    my_context['extra_url_context'] = context['extra_url_context']
    my_context['show'] = context['show']
    return my_context
register.inclusion_tag('appointment_row.html', takes_context=True)(render_appointment_row)


class ModelPk(template.Node):
    def __init__(self, contenttype, visit_model, appointment, dashboard_type, app_label):
        self.unresolved_contenttype = template.Variable(contenttype)
        self.unresolved_appointment = template.Variable(appointment)
        self.unresolved_visit_model = template.Variable(visit_model)
        self.unresolved_dashboard_type = template.Variable(dashboard_type)
        self.unresolved_app_label = template.Variable(app_label)

    def render(self, context):
        self.contenttype = self.unresolved_contenttype.resolve(context)
        self.appointment = self.unresolved_appointment.resolve(context)
        self.visit_model = self.unresolved_visit_model.resolve(context)
        self.visit_model_instance = None
        pk = None
        try:
            appointment_0 = self.appointment.__class__.objects.get(
                registered_subject=self.appointment.registered_subject,
                visit_definition=self.appointment.visit_definition,
                visit_instance=0)
        except:
            raise TypeError('Registered Subject Dashboard Template tag expected appointment, Got None.')
        if self.visit_model.__class__.objects.filter(appointment=self.appointment).exists():
            self.visit_model_instance = self.visit_model.__class__.objects.get(appointment=appointment_0)
        model_cls = self.contenttype.model_class()
        visit_attr = VisitModelHelper().get_visit_field(model=model_cls, visit_model=self.visit_model)
        if not visit_attr:
            raise AttributeError('Cannot determine pk with this templatetag, Model %s must have a '
                                 'foreignkey to the visit model \'%s\'.')
        # query model_cls for visit=this_visit, or whatever the fk_fieldname is
        # i have to use 'extra' because i can only know the fk field name pointing to the visit model at runtime
        if self.visit_model_instance:
            if model_cls.objects.filter(**{visit_attr: self.visit_model_instance}).exists():
                # the link is for a change
                # these next two lines would change if for another dashboard and another visit model
                model_instance = model_cls.objects.get(**{visit_attr: self.visit_model_instance})
                pk = model_instance.pk
        return pk


@register.tag(name='model_pk')
def model_pk(parser, token):
    """Returns pk for model instance related to this visit model instance."""
    try:
        _, contenttype, visit_model, appointment, dashboard_type, app_label = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly 5 arguments" % token.contents.split()[0])
    return ModelPk(contenttype, visit_model, appointment, dashboard_type, app_label)


class ModelAdminUrl(template.Node):

    """return a reverse url to admin + '?dashboard-specific querystring'
    for 'change' or 'add' for a given contenttype model name"""

    def __init__(self, contenttype, visit_attr, next_url, dashboard_type,
                 dashboard_model, dashboard_id, show, extra_url_context):
        self.unresolved_contenttype = template.Variable(contenttype)
        self.unresolved_next_url = template.Variable(next_url)
        self.unresolved_dashboard_type = template.Variable(dashboard_type)
        self.unresolved_dashboard_model = template.Variable(dashboard_model)
        self.unresolved_dashboard_id = template.Variable(dashboard_id)
        self.unresolved_show = template.Variable(show)
        self.unresolved_extra_url_context = template.Variable(extra_url_context)
        self.unresolved_visit_attr = template.Variable(visit_attr)

    def render(self, context):
        self.contenttype = self.unresolved_contenttype.resolve(context)
        self.next_url = self.unresolved_next_url.resolve(context)
        self.dashboard_type = self.unresolved_dashboard_type.resolve(context)
        self.dashboard_model = self.unresolved_dashboard_model.resolve(context)
        self.dashboard_id = self.unresolved_dashboard_id.resolve(context)
        self.show = self.unresolved_show.resolve(context)
        self.extra_url_context = self.unresolved_extra_url_context.resolve(context)
        self.visit_attr = self.unresolved_visit_attr.resolve(context)
        if not self.extra_url_context:
            self.extra_url_context = ''
        model_cls = self.contenttype.model_class()
        if not self.visit_attr:
            raise AttributeError(
                'Cannot reverse for model, Model %s must have a foreignkey to the visit model \'%s\'. '
                'Check the model for the foreignkey and check the ModelAdmin class for line (visit_model=%s). '
                'Also check if this model is incorrectly referenced in '
                'bhp_visit.Entry.' % (model_cls._meta.object_name,
                                      self.visit_model._meta.object_name,
                                      self.visit_model._meta.object_name))
        if self.dashboard_model == 'visit':
            model_instance = model_cls.objects.get(**{self.visit_attr: self.dashboard_id})
        else:
            raise TypeError(
                'Expected attribute \'dashboard_model\' to be \'visit\'. Got {0}'.format(self.dashboard_model))
        if model_instance:
            url = reverse('admin:{app_label}_{model_name}_change'.format(
                app_label=model_cls._meta.app_label, model_name=model_cls._meta.object_name.lower()),
                args=(model_instance.pk,))
            rev_url = (
                '{url}?next={next}&dashboard_type={dashboard_type}&dashboard_model={dashboard_model}'
                '&dashboard_id={dashboard_id}&show={show}{extra_url_context}').format(
                    url=url,
                    next=self.next_url,
                    dashboard_type=self.dashboard_type,
                    dashboard_model=self.dashboard_model,
                    dashboard_id=self.dashboard_id,
                    show=self.show,
                    extra_url_context=self.extra_url_context)
        else:
            # the link is for an add
            try:
                url = reverse('admin:%s_%s_add' % (self.contenttype.app_label, self.contenttype.model))
                rev_url = (
                    '{url}?&next={next}&dashboard_type={dashboard_type}&dashboard_model={dashboard_model}'
                    '&dashboard_id={dashboard_id}&show={show}{extra_url_context}').format(
                        url=url,
                        next=self.next_url,
                        dashboard_type=self.dashboard_type,
                        dashboard_model=self.dashboard_model,
                        dashboard_id=self.dashboard_id,
                        show=self.show,
                        extra_url_context=self.extra_url_context)
            except:
                raise TypeError(
                    'NoReverseMatch while rendering reverse for %s_%s in admin_url_from_contenttype. '
                    'Is model registered in admin?' % (self.contenttype.app_label, self.contenttype.model))
        return rev_url


@register.tag(name='model_admin_url')
def model_admin_url(parser, token):
    """Compilation function for renderer ModelAdminUrl"""
    try:
        _, contenttype, visit_attr, next_url, dashboard_type, dashboard_model,\
            dashboard_id, show, extra_url_context = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires exactly 8 arguments (contenttype, visit_attr, next_url, "
            "dashboard_type, dashboard_model, dashboard_id, show, extra_url_context)" % token.contents.split()[0])
    return ModelAdminUrl(contenttype, visit_attr, next_url, dashboard_type,
                         dashboard_model, dashboard_id, show, extra_url_context)


class ModelAdminUrlFromRegisteredSubject(template.Node):

    """return a reverse url to admin + '?dashboard-specific querystring'
    for 'change' or 'add' for a given contenttype model name"""

    def __init__(self, contenttype, registered_subject, dashboard_type, app_label):
        self.unresolved_contenttype = template.Variable(contenttype)
        self.unresolved_registered_subject = template.Variable(registered_subject)
        self.unresolved_dashboard_type = template.Variable(dashboard_type)
        self.unresolved_app_label = template.Variable(app_label)

    def render(self, context):
        self.contenttype = self.unresolved_contenttype.resolve(context)
        self.registered_subject = self.unresolved_registered_subject.resolve(context)
        self.dashboard_type = self.unresolved_dashboard_type.resolve(context)
        self.app_label = self.unresolved_app_label.resolve(context)

        model_cls = self.contenttype.model_class()

        if model_cls.objects.filter(registered_subject=self.registered_subject).exists():
            # the link is for a change
            # these next two lines would change if for another dashboard and another visit model
            next_url_name = 'dashboard_url'
            model_instance = model_cls.objects.get(registered_subject=self.registered_subject)
            # do reverse url
            view = 'admin:%s_%s_change' % (model_cls._meta.app_label, model_cls._meta.module_name)
            view = str(view)
            rev_url = reverse(view, args=(model_instance.pk,))
            # add GET string to rev_url so that you will return to the dashboard
            # ...whence you came... assuming you catch "next" in change_view
            rev_url = '%s?next=%s&dashboard_type=%s&registered_subject=%s' % (
                rev_url, next_url_name, self.dashboard_type,
                self.registered_subject.pk)
        else:
            # the link is for an add
            next_url_name = 'dashboard_url'
            view = 'admin:%s_%s_add' % (self.contenttype.app_label, self.contenttype.model)
            view = str(view)
            rev_url = reverse(view)
            rev_url = '%s?next=%s&dashboard_type=%s&registered_subject=%s' % (
                rev_url,
                next_url_name, self.dashboard_type,
                self.registered_subject.pk)
        return rev_url


@register.tag(name='model_admin_url_from_registered_subject')
def model_admin_url_from_registered_subject(parser, token):
    """Compilation function for renderer ModelAdminUrlFromRegisteredSubject """
    try:
        _, contenttype, registered_subject, dashboard_type, app_label = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly 4 arguments" % token.contents.split()[0])
    return ModelAdminUrlFromRegisteredSubject(contenttype, registered_subject, dashboard_type, app_label)


class ModelPkFromRegisteredSubject(template.Node):
    def __init__(self, contenttype, registered_subject, dashboard_type, app_label):
        self.unresolved_contenttype = template.Variable(contenttype)
        self.unresolved_registered_subject = template.Variable(registered_subject)
        self.unresolved_dashboard_type = template.Variable(dashboard_type)
        self.unresolved_app_label = template.Variable(app_label)

    def render(self, context):
        self.contenttype = self.unresolved_contenttype.resolve(context)
        self.registered_subject = self.unresolved_registered_subject.resolve(context)
        self.dashboard_type = self.unresolved_dashboard_type.resolve(context)
        self.app_label = self.unresolved_app_label.resolve(context)
        pk = None
        model_cls = self.contenttype.model_class()
        if model_cls.objects.filter(registered_subject=self.registered_subject).exists():
            model_instance = model_cls.objects.get(registered_subject=self.registered_subject)
            pk = model_instance.pk
        return pk


@register.tag(name='model_pk_from_registered_subject')
def model_pk_from_registered_subject(parser, token):
    """return pk for model instance"""
    try:
        _, contenttype, registered_subject, dashboard_type, app_label = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly 4 arguments" % token.contents.split()[0])
    return ModelPkFromRegisteredSubject(contenttype, registered_subject, dashboard_type, app_label)
