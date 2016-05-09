from collections import OrderedDict, namedtuple, Counter

from django.core.exceptions import ImproperlyConfigured
from django.apps import apps
from django.db.utils import IntegrityError

from edc_configuration.models import GlobalConfiguration
from edc_content_type_map.models import ContentTypeMapHelper, ContentTypeMap
from edc_meta_data.models import CrfEntry, LabEntry, RequisitionPanel

from ..models import MembershipForm, Schedule, VisitDefinition


CrfTuple = namedtuple('CrfTuple', 'order app_label model_name default_entry_status additional')
MembershipFormTuple = namedtuple('MembershipFormTuple', 'name model visible')
RequisitionPanelTuple = namedtuple('RequisitionPanelTuple', 'entry_order app_label model_name '
                                   'requisition_panel_name panel_type aliquot_type_alpha_code '
                                   'default_entry_status additional')
ScheduleTuple = namedtuple('ScheduleTuple', 'name membership_form_name grouping_key comment')


class VisitScheduleConfiguration(object):
    """Creates or updates the membership_form, schedule, crf_entry,
    lab_entry models and visit_definition.

        .. note:: RequisitionPanel is needed for lab_entry but is
                 populated in the app_configuration and not here."""

    name = 'unnamed visit schedule'
    app_label = None
    membership_forms = OrderedDict()
    schedules = OrderedDict()
    visit_definitions = OrderedDict()

    def __init__(self):
        self.verify_dictionaries()
        if not GlobalConfiguration.objects.get_attr_value('sync_content_type_map'):
            self.sync_content_type_map()
        self.ready = False

    def __repr__(self):
        return '{0}.{1} {2}'.format(self.app_label, self.name, 'ready' if self.ready else 'not ready')

    def build(self):
        """Builds and / or updates the visit schedule models."""
        self.update_or_create_membership_forms()
        self.update_or_create_schedules()
        self.update_or_create_visit_definitions()
        self.ready = True

    def sync_content_type_map(self):
        """Repopulates and syncs the ContentTypeMap instances."""
        content_type_map_helper = ContentTypeMapHelper()
        content_type_map_helper.populate()
        content_type_map_helper.sync()
        GlobalConfiguration.objects.set_attr('sync_content_type_map', True)

    def verify_dictionaries(self):
        """Verifies some aspects of the the format of the dictionary attributes."""
        self.verify_membership_forms_dict()
        self.verify_schedules_dict()
        self.verify_visit_definitions_dict()

    def verify_membership_forms_dict(self):
        for membership_form in self.membership_forms.values():
            if not issubclass(membership_form.__class__, MembershipFormTuple):
                raise ImproperlyConfigured('Visit Schedule \'membership_forms\' '
                                           'must contain instances of the named tuple MembershipFormTuple. '
                                           'Got {0}'.format(membership_form))
        for name, membership_form in self.membership_forms.items():
            if not name == membership_form.name:
                raise ImproperlyConfigured('Visit Schedule \'membership_forms\' '
                                           'expects each dictionary key {0} to be in it\'s named tuple. '
                                           'Got {1}.'.format(name, membership_form.name))
        models = []
        for name, membership_form in self.membership_forms.items():
            models.append(membership_form.model)
        duplicates = [item for item, count in Counter(models).items() if count > 1]
        if duplicates:
            raise ImproperlyConfigured(
                'Visit Schedule \'membership_forms\' uses a membership form more than once. '
                'Got \'{}\'.'.format(
                    ', '.join(['{}.{}'.format(m._meta.app_label, m._meta.model_name) for m in duplicates])))

    def verify_schedules_dict(self):
        for schedule in self.schedules.values():
            if not issubclass(schedule.__class__, ScheduleTuple):
                raise ImproperlyConfigured('Visit Schedule \'schedules\' '
                                           'must contain instances of the named tuple ScheduleTuple. '
                                           'Got {0}'.format(schedule))
        for name, schedule in self.schedules.items():
            if not name == schedule.name:
                raise ImproperlyConfigured('Visit Schedule \'schedules\' '
                                           'expects each dictionary key {0} to be in it\'s named tuple. '
                                           'Got {1}.'.format(name, schedule.name))

        for schedule in self.schedules.values():
            if schedule.membership_form_name not in self.membership_forms:
                raise ImproperlyConfigured(
                    'Visit Schedule \'schedules\' has a scheduled not linked to '
                    'a membership_form. Got \'{0}\'. Add it to \'membership_forms\' '
                    'or correct \'scheduled_groups\'.'.format(schedule.membership_form_name))

    def verify_visit_definitions_dict(self):
        for visit_definition in self.visit_definitions.values():
            for crf in visit_definition.get('entries'):
                model = apps.get_model(crf.app_label, crf.model_name)
                if not model:
                    raise ImproperlyConfigured('Visit Schedule entries refers '
                                               'to a CRF model {0}.{1} which does not exist.'.format(
                                                   crf.app_label, crf.model_name))
                try:
                    model.entry_meta_data_manager
                except AttributeError:
                    raise ImproperlyConfigured(
                        'Visit Schedule entries model {}.{} is missing an '
                        'entry_meta_data_manager.'.format(crf.app_label, crf.model_name))
            for requisition in visit_definition.get('requisitions'):
                model = apps.get_model(requisition.app_label, requisition.model_name)
                if not model:
                    raise ImproperlyConfigured(
                        'Visit Schedule requisitions refers to model {0}.{1} which '
                        'does not exist.'.format(requisition.app_label, requisition.model_name))
                try:
                    model.entry_meta_data_manager
                except AttributeError:
                    raise ImproperlyConfigured('Visit Schedule requisition model {}.{} is missing '
                                               'an entry_meta_data_manager.'.format(
                                                   requisition.app_label, requisition.model_name))

    def update_or_create_membership_forms(self):
        for membership_form in self.membership_forms.values():
            try:
                obj = MembershipForm.objects.get(category=membership_form.name)
                obj.app_label = membership_form.model._meta.app_label
                obj.model_name = membership_form.model._meta.object_name
                obj.content_type_map = self.get_content_type_map(
                    membership_form.model._meta.app_label,
                    membership_form.model._meta.model_name)
                obj.visible = membership_form.visible
                obj.save()
            except MembershipForm.DoesNotExist:
                content_type_map = self.get_content_type_map(
                    membership_form.model._meta.app_label,
                    membership_form.model._meta.model_name)
                MembershipForm.objects.filter(content_type_map=content_type_map).delete()
                MembershipForm.objects.create(
                    category=membership_form.name,
                    app_label=membership_form.model._meta.app_label,
                    model_name=membership_form.model._meta.object_name,
                    content_type_map=content_type_map,
                    visible=membership_form.visible)

    def update_or_create_schedules(self):
        for group_name, schedule in self.schedules.items():
            try:
                obj = Schedule.objects.get(group_name=group_name)
                obj.group_name = group_name
                obj.membership_form = MembershipForm.objects.get(category=schedule.membership_form_name)
                obj.grouping_key = schedule.grouping_key
                obj.comment = schedule.comment
                obj.save()
            except Schedule.DoesNotExist:

                try:
                    membership_form = MembershipForm.objects.get(
                        category=schedule.membership_form_name)
                except MembershipForm.DoesNotExist as e:
                    raise ImproperlyConfigured('{}, {}'.format(schedule.membership_form_name, str(e)))

                Schedule.objects.create(
                    group_name=group_name,
                    membership_form=membership_form,
                    grouping_key=schedule.grouping_key,
                    comment=schedule.comment)

    def update_or_create_visit_definitions(self):
        for code, visit_definition in self.visit_definitions.items():
            visit_tracking_content_type_map = self.get_content_type_map(
                visit_definition.get('visit_tracking_model')._meta.app_label,
                visit_definition.get('visit_tracking_model')._meta.model_name)
            try:
                schedule = Schedule.objects.get(
                    group_name=visit_definition.get('schedule'))
            except Schedule.DoesNotExist:
                raise ImproperlyConfigured(
                    'Schedule group \'{}\' referred to in \'visit_definitions\' does not exist. '
                    'Add it to \'scheduled_groups\' or correct the visit definition.'.format(
                        visit_definition.get('schedule')))
            try:
                visit_definition_instance = VisitDefinition.objects.get(code=code)
                visit_definition_instance.code = code
                visit_definition_instance.title = visit_definition.get('title')
                visit_definition_instance.time_point = visit_definition.get('time_point')
                visit_definition_instance.base_interval = visit_definition.get('base_interval')
                visit_definition_instance.base_interval_unit = visit_definition.get('base_interval_unit')
                visit_definition_instance.lower_window = visit_definition.get('window_lower_bound')
                visit_definition_instance.lower_window_unit = visit_definition.get('window_lower_bound_unit')
                visit_definition_instance.upper_window = visit_definition.get('window_upper_bound')
                visit_definition_instance.upper_window_unit = visit_definition.get('window_upper_bound_unit')
                visit_definition_instance.grouping = visit_definition.get('grouping')
                visit_definition_instance.visit_tracking_content_type_map = visit_tracking_content_type_map
                visit_definition_instance.instruction = visit_definition.get('instructions') or '-'
                visit_definition_instance.save()
            except VisitDefinition.DoesNotExist:
                visit_definition_instance = VisitDefinition.objects.create(
                    code=code,
                    title=visit_definition.get('title'),
                    time_point=visit_definition.get('time_point'),
                    base_interval=visit_definition.get('base_interval'),
                    base_interval_unit=visit_definition.get('base_interval_unit'),
                    lower_window=visit_definition.get('window_lower_bound'),
                    lower_window_unit=visit_definition.get('window_lower_bound_unit'),
                    upper_window=visit_definition.get('window_upper_bound'),
                    upper_window_unit=visit_definition.get('window_upper_bound_unit'),
                    grouping=visit_definition.get('grouping'),
                    visit_tracking_content_type_map=visit_tracking_content_type_map,
                    instruction=visit_definition.get('instructions') or '-')
            finally:
                visit_definition_instance.schedule.add(schedule)
            self.update_or_create_crf_entries(visit_definition, visit_definition_instance)
            self.update_or_create_lab_entries(visit_definition, visit_definition_instance)

    def update_or_create_crf_entries(self, visit_definition, visit_definition_instance):
        for item in visit_definition.get('entries'):
            content_type_map = self.get_content_type_map(item.app_label, item.model_name)
            try:
                crf_entry = CrfEntry.objects.get(
                    app_label=item.app_label,
                    model_name=item.model_name.lower(),
                    visit_definition=visit_definition_instance)
                crf_entry.entry_order = item.order
                crf_entry.default_entry_status = item.default_entry_status
                crf_entry.additional = item.additional
                crf_entry.save(update_fields=['entry_order', 'default_entry_status', 'additional'])
            except CrfEntry.DoesNotExist:
                CrfEntry.objects.create(
                    content_type_map=content_type_map,
                    visit_definition=visit_definition_instance,
                    entry_order=item.order,
                    app_label=item.app_label.lower(),
                    model_name=item.model_name.lower(),
                    default_entry_status=item.default_entry_status,
                    additional=item.additional)
        for crf_entry in CrfEntry.objects.filter(visit_definition=visit_definition_instance):
            model_tpls = []
            for item in visit_definition.get('entries'):
                model_tpls.append((item.app_label.lower(), item.model_name.lower()))
            if (crf_entry.app_label.lower(), crf_entry.model_name.lower()) not in model_tpls:
                pass

    def update_or_create_lab_entries(self, visit_definition, visit_definition_instance):
        for item in visit_definition.get('requisitions'):
            # requisition panel must exist, see app_configuration
            try:
                requisition_panel = RequisitionPanel.objects.get(
                    name=item.requisition_panel_name)
            except RequisitionPanel.DoesNotExist:
                raise ImproperlyConfigured(
                    'RequisitionPanel matching query does not exist, '
                    'for name=\'{}\'. Re-run app_configuration.'
                    'prepare() or check the config.'.format(item.requisition_panel_name))
            try:
                lab_entry = LabEntry.objects.get(
                    requisition_panel=requisition_panel,
                    visit_definition=visit_definition_instance)
                lab_entry.app_label = item.app_label
                lab_entry.model_name = item.model_name
                lab_entry.entry_order = item.entry_order
                lab_entry.default_entry_status = item.default_entry_status
                lab_entry.additional = item.additional
                lab_entry.save(update_fields=[
                    'app_label', 'model_name', 'entry_order', 'default_entry_status', 'additional'])
            except LabEntry.DoesNotExist:
                try:
                    LabEntry.objects.create(
                        app_label=item.app_label,
                        model_name=item.model_name,
                        requisition_panel=requisition_panel,
                        visit_definition=visit_definition_instance,
                        entry_order=item.entry_order,
                        default_entry_status=item.default_entry_status,
                        additional=item.additional)
                except IntegrityError:
                    raise IntegrityError(
                        '{} {} {}.{}'.format(
                            visit_definition_instance, requisition_panel,
                            item.app_label, item.model_name,))
        for lab_entry in LabEntry.objects.filter(visit_definition=visit_definition_instance):
            model_tpls = [
                (item.app_label, item.model_name) for item in visit_definition.get('requisitions')]
            if (lab_entry.app_label, lab_entry.model_name) not in model_tpls:
                lab_entry.delete()

    def get_content_type_map(self, app_label, model_name):
        try:
            content_type_map = ContentTypeMap.objects.get(
                app_label=app_label,
                module_name__iexact=model_name)
        except ContentTypeMap.DoesNotExist as e:
            raise ContentTypeMap.DoesNotExist(
                '{} Check INSTALLED_APPS for an APP '
                'that is referenced but not installed. Got {}.{}.'.format(str(e), app_label, model_name))
        return content_type_map
