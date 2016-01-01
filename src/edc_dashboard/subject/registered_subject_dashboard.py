from __future__ import print_function

from textwrap import wrap

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import TextField, Count
from django.template.loader import render_to_string

from edc_configuration.models import GlobalConfiguration
from edc.data_manager.models import ActionItem
from edc.data_manager.models import TimePointStatus
from edc_meta_data.helpers import CrfMetaDataHelper, RequisitionMetaDataHelper
from edc_lab.lab_clinic_api.classes import EdcLabResults
from edc_lab.lab_packing.models import PackingListMixin
from edc_lab.lab_requisition.models import RequisitionModelMixin
from edc.subject.lab_tracker.classes import site_lab_tracker
from edc_locator.models import LocatorMixin
from edc.subject.subject_summary.models import Link
from edc_appointment.models import Appointment, SubjectConfiguration
from edc_base.encrypted_fields import EncryptedTextField
from edc_base.utils import convert_from_camel
from edc_constants.constants import NEW, NOT_REQUIRED, UNKEYED, KEYED, NEW_APPT, COMPLETE_APPT, IN_PROGRESS
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.classes import MembershipFormHelper
from edc_visit_schedule.models import MembershipForm
from edc_visit_tracking.models import VisitModelMixin

from ..dashboard import Dashboard

from .crf_context import CrfContext
from .requisition_context import RequisitionContext


class RegisteredSubjectDashboard(Dashboard):

    dashboard_url_name = 'subject_dashboard_url'
    urlpatterns = [Dashboard.urlpatterns[0][:-1] + '(?P<show>{show})/$'] + Dashboard.urlpatterns
    urlpattern_options = dict(
        Dashboard.urlpattern_options,
        dashboard_model='household_member|visit|appointment|registered_subject',
        dashboard_type='subject',
        show='appointments|forms')

    def __init__(self, **kwargs):
        super(RegisteredSubjectDashboard, self).__init__(**kwargs)
        self._appointment = None
        self._appointment_zero = None
        self._appointment_continuation_count = None
        self._registered_subject = None
        self.appointment_row_template = 'appointment_row.html'
        self.membership_form_category = []
        self.visit_messages = []
        self.exclude_others_if_keyed_model_name = ''
        self.is_dispatched, self.dispatch_producer = False, None
        self.has_requisition_model = True
        self.dashboard_models['appointment'] = Appointment
        self.dashboard_models['registered_subject'] = RegisteredSubject

    def get_context_data(self, **kwargs):
        self.context = super(RegisteredSubjectDashboard, self).get_context_data(**kwargs)
        self.context.update(self.base_rendered_context)
        self.context.update(
            appointment=self.appointment,
            appointment_row_template=self.appointment_row_template,
            appointment_visit_attr=self.visit_model._meta.object_name.lower(),
            appointments=self.appointments,
            extra_url_context=self.extra_url_context,
            form_language_code=self.language,
            keyed_membership_forms=self.keyed_subject_membership_models,
            membership_forms=self.subject_membership_models,
            registered_subject=self.registered_subject,
            subject_configuration=self.subject_configuration,
            subject_dashboard_url=self.dashboard_url_name,
            subject_hiv_history=self.subject_hiv_history,
            subject_hiv_status=self.render_subject_hiv_status(),
            subject_identifier=self.subject_identifier,
            unkeyed_membership_forms=self.unkeyed_subject_membership_models,
            visit_attr=convert_from_camel(self.visit_model._meta.object_name),
            visit_code=self.visit_code,
            visit_instance=self.appointment_continuation_count,
            visit_messages=self.visit_messages,
            visit_model=self.visit_model,
            visit_model_admin_url_changelist='admin:{}_{}_changelist'.format(
                self.visit_model._meta.app_label, self.visit_model._meta.object_name.lower()),
            visit_model_admin_url_change='admin:{}_{}_change'.format(
                self.visit_model._meta.app_label, self.visit_model._meta.object_name.lower()),
            visit_model_admin_url_add='admin:{}_{}_add'.format(
                self.visit_model._meta.app_label, self.visit_model._meta.object_name.lower()),
            visit_model_instance=self.visit_model_instance,
            time_point_status=self.time_point_status,
        )
        if self.show == 'forms':
            self.context.update(
                requisition_model=self.requisition_model,
                rendered_scheduled_forms=self.rendered_scheduled_forms,
            )
            if self.requisition_model:
                self.context.update(requisition_model_meta=self.requisition_model._meta)
                self.context.update(rendered_scheduled_requisitions=self.rendered_requisitions)
            self.render_summary_links()
        self.context.update(rendered_action_items=self.render_action_item())
        self.context.update(rendered_locator=self.render_locator())
        self.context.update(self.lab_results_data())
        return self.context

    @property
    def show(self):
        return self.context.get('show', 'appointments')

    @property
    def home_url(self):
        """Returns a home url."""
        return reverse(
            self.dashboard_url_name,
            kwargs={'dashboard_type': self.dashboard_type,
                    'dashboard_model': self.dashboard_model_name,
                    'dashboard_id': self.dashboard_id,
                    'show': 'forms'})

    def verify_dashboard_model(self, value):
        """Verify the dashboard model has a way to get to registered_subject."""
        for model in value.itervalues():
            if model:
                if 'get_registered_subject' not in dir(model):
                    raise ImproperlyConfigured(
                        'RegisteredSubjectDashboard dashboard_model {0} must '
                        'have method registered_subject. See {1}.'.format(model, self))

    def add_visit_message(self, message):
        self.visit_messages.append(message)

    @property
    def visit_code(self):
        try:
            return self.appointment.visit_definition.code
        except AttributeError:
            return None

    @property
    def consent(self):
        return None

    @property
    def subject_hiv_status(self):
        """Returns to the value returned by the site_lab_tracker for this registered subject."""
        self._subject_hiv_status = None
        if self.registered_subject:
            self._subject_hiv_status = site_lab_tracker.get_current_value(
                'HIV', self.registered_subject.subject_identifier, self.registered_subject.subject_type)[0]
        return self._subject_hiv_status

    @property
    def subject_hiv_history(self):
        """Returns to the value returned by the site_lab_tracker for this registered subject."""
        self._subject_hiv_history = None
        if self.registered_subject:
            # TODO: this gets hit on every dashboard refresh and is very SLOW
            self._subject_hiv_history = site_lab_tracker.get_history_as_string(
                'HIV', self.registered_subject.subject_identifier, self.registered_subject.subject_type)
        return self._subject_hiv_history

    @property
    def registered_subject(self):
        if not self._registered_subject:
            try:
                self._registered_subject = RegisteredSubject.objects.get(pk=self.dashboard_id)
            except RegisteredSubject.DoesNotExist:
                try:
                    self._registered_subject = self.dashboard_model_instance.registered_subject
                except AttributeError:
                    try:
                        self._registered_subject = self.dashboard_model_instance.appointment.registered_subject
                    except AttributeError:
                        pass
        return self._registered_subject

    @property
    def appointment(self):
        if not self._appointment:
            if self.dashboard_model_name == 'appointment':
                self._appointment = Appointment.objects.get(pk=self.dashboard_id)
            elif self.dashboard_model_name == 'visit':
                self._appointment = self.visit_model.objects.get(pk=self.dashboard_id).appointment
            else:
                self._appointment = None
            self._appointment_zero = None
            self._appointment_continuation_count = None
        return self._appointment

    @property
    def appointment_zero(self):
        if not self._appointment_zero:
            if self.appointment:
                if self.appointment.visit_instance == '0':
                    self._appointment_zero = self.appointment
                else:
                    if Appointment.objects.filter(
                            registered_subject=self.appointment.registered_subject,
                            visit_definition=self.appointment.visit_definition, visit_instance=0) > 1:
                        self.delete_duplicate_appointments(inst=self)
                    self._appointment_zero = Appointment.objects.get(
                        registered_subject=self.appointment.registered_subject,
                        visit_definition=self.appointment.visit_definition,
                        visit_instance=0)
        return self._appointment_zero

    @property
    def appointment_continuation_count(self):
        if not self._appointment_continuation_count:
            if self.appointment:
                self._appointment_continuation_count = self._appointment.visit_instance
        return self._appointment_continuation_count

    @classmethod
    def delete_duplicate_appointments(cls, inst=None, visit_model=None):
        """Deletes all but one duplicate appointments as long as they are not related to a visit model."""
        if not visit_model:
            visit_model = inst.visit_model
        appointments = Appointment.objects.values(
            'registered_subject__pk', 'visit_definition', 'visit_instance').all().annotate(
                num=Count('pk')).order_by()
        dups = [a for a in appointments if a.get('num') > 1]
        for dup in dups:
            num = dup['num']
            del dup['num']
            for dup_appt in Appointment.objects.filter(**dup):
                if not visit_model.objects.filter(appointment=dup_appt):
                    try:
                        dup_appt.delete()
                        num -= 1
                    except:
                        pass
                    if num == 1:
                        break  # leave one

    @property
    def appointments(self):
        """Returns all appointments for this registered_subject or just one
        if given a appointment_code and appointment_continuation_count.

        Could show
            one
            all
            only for this membership form category (which is the subject type)
            only those for a given membership form
            only those for a visit definition grouping
            """
        appointments = []
        if self.show == 'forms':
            appointments = [self.appointment]
        else:
            # or filter appointments for the current membership categories
            # schedule_group__membership_form
            codes = []
            for category in self.membership_form_category:
                codes.extend(MembershipForm.objects.codes_for_category(membership_form_category=category))
                appointments = Appointment.objects.filter(
                    registered_subject=self.registered_subject,
                    visit_definition__code__in=codes).order_by(
                    'visit_definition__time_point', 'visit_instance', 'appt_datetime')
        return appointments

    @property
    def visit_model(self):
        return self._visit_model

    @visit_model.setter
    def visit_model(self, visit_model):
        self._visit_model = visit_model
        if not self._visit_model:
            raise TypeError('Attribute _visit_model may not be None. Override the method '
                            'to return a visit mode class or specify at init.')
        if not issubclass(self._visit_model, VisitModelMixin):
            raise TypeError('Expected visit model class to be a subclass of '
                            'VisitTrackingModelMixin. Got {0}. See {1}.'.format(self._visit_model, self))

    @property
    def visit_model_attrname(self):
        """Returns what is assumed to be the field name for the visit model in
        appointment based on the visit model object name."""
        return convert_from_camel(self.visit_model._meta.object_name)

    @property
    def visit_model_rel_attrname(self):
        """Returns what is assumed to be the field name for the visit model in
        appointment based on the visit model object name."""
        return self.visit_model._meta.object_name.lower()

    @property
    def visit_model_instance(self):
        """Returns the visit model instance but may be None."""
        self._visit_model_instance = None
        try:
            self._visit_model_instance = self.visit_model.objects.get(appointment=self.appointment)
        except self.visit_model.DoesNotExist:
            try:
                self._visit_model_instance = self.visit_model.objects.get(pk=self.dashboard_id)
            except self.visit_model.DoesNotExist:
                pass
        if self._visit_model_instance:
            if not isinstance(self._visit_model_instance, self.visit_model):
                raise TypeError('Expected an instance of visit model class {0}.'.format(self.visit_model))
        return self._visit_model_instance

    @property
    def requisition_model(self):
        return self._requisition_model

    @requisition_model.setter
    def requisition_model(self, requisition_model):
        self._requisition_model = requisition_model
        if self.has_requisition_model:
            if not self._requisition_model:
                raise TypeError('Attribute _requisition model cannot be None. See {0}'.format(self))
            if not issubclass(self._requisition_model, RequisitionModelMixin):
                raise TypeError('Expected a subclass of RequisitionModelMixin. '
                                'Got {0}. See {1}.'.format(self._requisition_model, self))

    @property
    def packing_list_model(self):
        return self._packing_list_model

    @packing_list_model.setter
    def packing_list_model(self):
        self._packing_list_model = self.packing_list_model
        if not self._packing_list_model:
            raise TypeError(
                'Attribute \'_packing_list_model\' may not be None. '
                'Override the getter. See {0}'.format(self))
        if not issubclass(self._packing_list_model, PackingListMixin):
            raise TypeError(
                'Expected a subclass of BasePackingList. Got {0}. See {1}.'.format(
                    self._packing_list_model, self))

    @property
    def subject_membership_models(self):
        """Sets to a dictionary of membership "models" that are
        keyed model instances and unkeyed model classes.

        Membership forms can also be proxy models ... see mochudi_subject.models."""
        helper = MembershipFormHelper()
        self._subject_membership_models = []
        for category in self.membership_form_category:
            self._subject_membership_models.append(
                helper.get_membership_models_for(
                    self.registered_subject,
                    category,
                    extra_grouping_key=self.exclude_others_if_keyed_model_name
                )
            )
        return self._subject_membership_models

    @property
    def keyed_subject_membership_models(self):
        keyed = []
        for member_model in self.subject_membership_models:
            keyed.extend(member_model.get('keyed'))
        return keyed

    @property
    def unkeyed_subject_membership_models(self):
        unkeyed = []
        for member_model in self.subject_membership_models:
            unkeyed.extend(member_model.get('unkeyed'))
        return unkeyed

    @property
    def subject_type(self):
        return self.registered_subject.subject_type

    @property
    def subject_identifier(self):
        self._subject_identifier = None
        if self.registered_subject:
            self._subject_identifier = self.registered_subject.subject_identifier
        return self._subject_identifier

    @property
    def subject_configuration(self):
        self._subject_configuration = None
        if self.subject_identifier:
            if SubjectConfiguration.objects.filter(subject_identifier=self.subject_identifier):
                self._subject_configuration = SubjectConfiguration.objects.get(
                    subject_identifier=self.subject_identifier)
        return self._subject_configuration

    @property
    def time_point_status(self):
        self._time_point_status = None
        if self.appointment:
            try:
                self._time_point_status = TimePointStatus.objects.get(appointment=self.appointment)
            except TimePointStatus.DoesNotExist:
                pass
        return self._time_point_status

    def render_summary_links(self, template_filename=None):
        """Renders the side bar template for subject summaries."""
        if not template_filename:
            template_filename = 'summary_side_bar.html'
        summary_links = render_to_string(template_filename, {
            'links': Link.objects.filter(dashboard_type=self.dashboard_type),
            'subject_identifier': self.subject_identifier})
        self.context.update(summary_links=summary_links)

    def render_labs(self):
        """Renders labs for the template side bar if the
        requisition model is set, by default will not update.

        .. seealso:: :class:`lab_clinic_api.classes.EdcLabResults`"""

        if self._requisition_model:
            edc_lab_results = EdcLabResults()
            return edc_lab_results.render(self.subject_identifier, False)
        return ''

    def lab_results_data(self):
        """Achieves almost the same end result with the render_labs
        method above but depends on template inclusion"""
        return EdcLabResults().context_data(self.subject_identifier, False) if self._requisition_model else {}

    @property
    def locator_model(self):
        return self._locator_model

    @locator_model.setter
    def locator_model(self, model):
        """Sets the locator model class which must be a
        subclass of edc.subject.locator.BaseLocator."""
        self._locator_model = model
        if self._locator_model:
            if not issubclass(self._locator_model, LocatorMixin):
                raise TypeError('Locator model must be a subclass of BaseLocator. See {0}'.format(self))

    @property
    def locator_inst(self):
        """Sets to a locator model instance for the registered_subject."""
        self._locator_inst = None
        if self.locator_model:
            if self.locator_model.objects.filter(registered_subject=self.locator_registered_subject):
                self._locator_inst = self.locator_model.objects.get(
                    registered_subject=self.locator_registered_subject)
        return self._locator_inst

    @property
    def locator_registered_subject(self):
        """Users may override to return a registered_subject other than
        the current or None -- used to filter the locator model.

        For example, current subject is an infant, need mother\'s
        registered subject instance to filter Locator model."""
        return self.registered_subject

    @property
    def locator_visit_model(self):
        """Users may override to return a visit_model other than the
        current or None -- used to filter the locator model."""
        return self.visit_model

    @property
    def locator_visit_model_attrname(self):
        return convert_from_camel(self.locator_visit_model._meta.object_name)  # ??

    @property
    def locator_scheduled_visit_code(self):
        """ Returns visit where the locator is scheduled,
        TODO: maybe search visit definition for this?."""
        return None

    @property
    def locator_template(self):
        """Users may override to return a custom locator template."""
        return 'locator_include.html'

    @property
    def subject_hiv_template(self):
        return 'subject_hiv_status.html'

    def render_locator(self):
        """Renders to string the locator for the current locator instance if it is set.

        .. note:: getting access to the correct visit model instance for the locator
                  is a bit tricky. locator model is usually scheduled once for the
                  subject type and otherwise edited from the dashboard sidebar. It may
                  also be 'added' from the dashboard sidebar. Either way, the visit model
                  instance is required -- that being the instance that was (or would
                  have been) used if updated as a scheduled form. If the dashboard is
                  in appointments mode, there is no selected visit model instance.
                  Similarly, if the locator is edited from another dashboard, such as
                  the infant dashboard with maternal/infant pairs, the maternal visit
                  instance is not known. Some methods may be overriden to solve this.
                  They all have 'locator' in the name."""
        context = self.base_rendered_context
        if self.locator_model:
            locator_add_url = None
            locator_change_url = None
            if not self.locator_inst:
                context.update({'locator': None})
                locator_add_url = reverse(
                    'admin:{}_{}_add'.format(
                        self.locator_model._meta.app_label, self.locator_model._meta.module_name))
            if self.locator_inst:
                context.update({'locator': self.locator_inst})
                locator_change_url = reverse(
                    'admin:{}_{}_change'.format(
                        self.locator_model._meta.app_label,
                        self.locator_model._meta.module_name), args=(self.locator_inst.pk, ))
                for field in self.locator_inst._meta.fields:
                    if isinstance(field, (TextField)):
                        value = getattr(self.locator_inst, field.name)
                        if value:
                            setattr(self.locator_inst, field.name, '<BR>'.join(wrap(value, 25)))
        context.update({
            'subject_dashboard_url': self.dashboard_url_name,
            'dashboard_type': self.dashboard_type,
            'dashboard_model': self.dashboard_model_name,
            'dashboard_id': self.dashboard_id,
            'show': self.show,
            'registered_subject': self.registered_subject,
            'visit_attr': self.visit_model_attrname,
            'visit_model_instance': self.visit_model_instance,
            'appointment': self.appointment,
            'locator_add_url': locator_add_url,
            'locator_change_url': locator_change_url})
        # subclass may insert / update context values (e.g. visit stuff)
        context = self.update_locator_context(context)
        return render_to_string(self.locator_template, context)

    def update_locator_context(self, context):
        """Update context to set visit information if needing something other than the default."""
        context.update(self.base_rendered_context)
        if context.get('visit_model_instance'):
            if not isinstance(context.get('visit_model_instance'), self.locator_visit_model):
                context['visit_model_instance'] = None
        if not context.get('visit_model_instance'):
            if self.locator_inst:
                visit_model_instance = getattr(self.locator_inst, self.locator_visit_model_attrname)
            else:
                locator_visit_code = self.locator_scheduled_visit_code
                visit_model_instance = None
                if self.locator_model.objects.filter(registered_subject=self.locator_registered_subject):
                    visit_model_instance = self.locator_model.objects.get(
                        registered_subject=self.locator_registered_subject).maternal_visit
                elif self.locator_visit_model.objects.filter(
                        appointment__registered_subject=self.locator_registered_subject,
                        appointment__visit_definition__code=locator_visit_code, appointment__visit_instance=0):
                    visit_model_instance = self.locator_visit_model.objects.get(
                        appointment__registered_subject=self.locator_registered_subject,
                        appointment__visit_definition__code=locator_visit_code, appointment__visit_instance=0)
                else:
                    pass
            if visit_model_instance:
                context.update({'visit_attr': convert_from_camel(visit_model_instance._meta.object_name),
                                'visit_model_instance': visit_model_instance})
        return context

    def render_action_item(self, action_item_cls=None, template=None, **kwargs):
        """Renders to string the action_items for the current registered subject."""
        source_registered_subject = kwargs.get('registered_subject', self.registered_subject)
        action_item_cls = action_item_cls or ActionItem
        if isinstance(action_item_cls, models.Model):
            raise TypeError(
                'Expected first parameter to be a Action Item model class. '
                'Got an instance. Please correct in local dashboard view.')
        if not template:
            template = 'action_item_include.html'
        action_items = action_item_cls.objects.filter(
            registered_subject=source_registered_subject, display_on_dashboard=True, status='Open')
        action_item_instances = []
        if action_items:
            for action_item in action_items:
                for field in action_item._meta.fields:
                    if isinstance(field, (TextField, EncryptedTextField)):
                        value = getattr(action_item, field.name)
                        if value:
                            setattr(action_item, field.name, '<BR>'.join(wrap(value, 25)))
                action_item_instances.append(action_item)
        if action_item_instances:
            self.context.update(
                action_item_message=('Action items exist for this subject. '
                                     'Please review and resolve if possible.'))
        else:
            self.context.update(action_item_message=None)
        self.context.update(self.base_rendered_context)
        self.context.update({
            'action_items': action_item_instances,
            'registered_subject': self.registered_subject,
            'dashboard_type': self.dashboard_type,
            'dashboard_model': self.dashboard_model_name,
            'dashboard_id': self.dashboard_id,
            'show': self.show,
            'action_item_meta': action_item_cls._meta})
        rendered_action_items = render_to_string(template, self.context)
        return rendered_action_items

    @property
    def rendered_scheduled_forms(self):
        """Renders the Crf Forms section of the dashboard
        using the context class CrfContext."""
        template = 'crf_entries.html'
        crf_entries = []
        crf_meta_data_helper = CrfMetaDataHelper(
            self.appointment_zero, self.visit_model_instance, self.visit_model_attrname)
        for meta_data_instance in crf_meta_data_helper.get_meta_data():
            crf_context = CrfContext(
                meta_data_instance, self.appointment, self.visit_model)
            crf_entries.append(crf_context.context)
        context = self.base_rendered_context
        context.update({
            'crf_entries': crf_entries,
            'visit_attr': self.visit_model_attrname,
            'visit_model_instance': self.visit_model_instance,
            'app_label': self.visit_model_instance._meta.app_label,
            'registered_subject': self.registered_subject.pk,
            'appointment': self.appointment.pk,
            'dashboard_type': self.dashboard_type,
            'dashboard_model': self.dashboard_model_name,
            'dashboard_id': self.dashboard_id,
            'subject_dashboard_url': self.dashboard_url_name,
            'show': self.show})
        rendered_scheduled_forms = render_to_string(template, context)
        return rendered_scheduled_forms

    @property
    def rendered_requisitions(self):
        """Renders the Scheduled Requisitions section of the dashboard
        using the context class RequisitionContext."""
        template = 'scheduled_requisitions.html'
        scheduled_requisitions = []
        not_required_requisitions = []
        additional_requisitions = []
        show_not_required_requisitions = GlobalConfiguration.objects.get_attr_value('show_not_required_requisitions')
        allow_additional_requisitions = GlobalConfiguration.objects.get_attr_value('allow_additional_requisitions')
        show_drop_down_requisitions = GlobalConfiguration.objects.get_attr_value('show_drop_down_requisitions')
        requisition_helper = RequisitionMetaDataHelper(
            self.appointment, self.visit_model_instance, self.visit_model_attrname)
        for scheduled_requisition in requisition_helper.get_meta_data():
            requisition_context = RequisitionContext(
                scheduled_requisition, self.appointment, self.visit_model, self.requisition_model)
            if (not show_not_required_requisitions and
                    not requisition_context.required and not requisition_context.additional):
                not_required_requisitions.append(requisition_context.context)
            elif (allow_additional_requisitions and not
                    requisition_context.required and requisition_context.additional):
                additional_requisitions.append(requisition_context.context)
            else:
                scheduled_requisitions.append(requisition_context.context)
        context = self.base_rendered_context
        context.update({
            'scheduled_requisitions': scheduled_requisitions,
            'additional_requisitions': additional_requisitions,
            'drop_down_list_requisitions': self.drop_down_list_requisitions(scheduled_requisitions),
            'show_drop_down_requisitions': show_drop_down_requisitions,
            'visit_attr': self.visit_model_attrname,
            'visit_model_instance': self.visit_model_instance,
            'registered_subject': self.registered_subject.pk,
            'appointment': self.appointment.pk,
            'dashboard_type': self.dashboard_type,
            'dashboard_model': self.dashboard_model_name,
            'dashboard_id': self.dashboard_id,
            'subject_dashboard_url': self.dashboard_url_name,
            'show': self.show})
        rendered_requisitions = render_to_string(template, context)
        return rendered_requisitions

    def drop_down_list_requisitions(self, scheduled_requisitions):
        drop_down_list_requisitions = []
        for requisition in scheduled_requisitions:
            lab_entry = requisition['lab_entry']
            meta_data_status = requisition['status']
            meta_data_required = meta_data_status != 'NOT_REQUIRED'
            if lab_entry.not_required and not lab_entry.additional:
                continue
            if not meta_data_required:
                drop_down_list_requisitions.append(requisition)
        return drop_down_list_requisitions

    def render_subject_hiv_status(self):
        """Renders to string a to a url to the historymodel for the subject_hiv_status."""
        if self.subject_hiv_status:
            change_list_url = reverse('admin:lab_tracker_historymodel_changelist')
            context = self.base_rendered_context
            context.update({
                'subject_hiv_status': self.subject_hiv_status,
                'subject_identifier': self.subject_identifier,
                'subject_type': self.subject_type,
                'change_list_url': change_list_url})
            return render_to_string(self.subject_hiv_template, context)
        return ''

    @property
    def base_rendered_context(self):
        return dict(
            IN_PROGRESS=IN_PROGRESS,
            NEW=NEW,
            KEYED=KEYED,
            UNKEYED=UNKEYED,
            NOT_REQUIRED=NOT_REQUIRED,
            NEW_APPT=NEW_APPT,
            COMPLETE_APPT=COMPLETE_APPT)
