from collections import OrderedDict, namedtuple

from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model

from edc.apps.app_configuration.exceptions import AppConfigurationError
from edc.core.bhp_content_type_map.classes import ContentTypeMapHelper
from edc.core.bhp_content_type_map.models import ContentTypeMap
from django.db.utils import IntegrityError

EntryTuple = namedtuple('EntryTuple', 'order app_label model_name default_entry_status additional')
MembershipFormTuple = namedtuple('MembershipFormTuple', 'name model visible')
RequisitionPanelTuple = namedtuple('RequisitionPanelTuple', 'entry_order app_label model_name '
                                   'requisition_panel_name panel_type aliquot_type_alpha_code '
                                   'default_entry_status additional')
ScheduleGroupTuple = namedtuple('ScheduleTuple', 'name membership_form_name grouping_key comment')


class VisitScheduleConfiguration(object):
    """Creates or updates the membership_form, schedule_group, entry,
    lab_entry models and visit_definition.

        .. note:: RequisitionPanel is needed for lab_entry but is
                 populated in the app_configuration and not here."""

    name = 'unnamed visit schedule'
    app_label = None
    membership_forms = OrderedDict()
    schedule_groups = OrderedDict()
    visit_definitions = OrderedDict()

    def __init__(self):
        self.sync_content_type_map_tries = 0

    def __repr__(self):
        return '{0}.{1}'.format(self.app_label, self.name)

    def verify(self):
        """Verifies some aspects of the the format of the dictionary attributes."""
        for membership_form in self.membership_forms.itervalues():
            if not issubclass(membership_form.__class__, MembershipFormTuple):
                raise ImproperlyConfigured('Visit Schedule Configuration attribute membership_forms '
                                           'must contain instances of the named tuple MembershipFormTuple. '
                                           'Got {0}'.format(membership_form))
        for schedule_group in self.schedule_groups.itervalues():
            if not issubclass(schedule_group.__class__, ScheduleGroupTuple):
                raise ImproperlyConfigured('Visit Schedule Configuration attribute schedule_groups '
                                           'must contain instances of the named tuple ScheduleGroupTuple. '
                                           'Got {0}'.format(schedule_group))
        for name, membership_form in self.membership_forms.iteritems():
            if not name == membership_form.name:
                raise ImproperlyConfigured('Visit Schedule Configuration attribute membership_forms '
                                           'expects each dictionary key {0} to be in it\'s named tuple. '
                                           'Got {1}.'.format(name, membership_form.name))
        for name, schedule_group in self.schedule_groups.iteritems():
            if not name == schedule_group.name:
                raise ImproperlyConfigured('Visit Schedule Configuration attribute schedule_groups '
                                           'expects each dictionary key {0} to be in it\'s named tuple. '
                                           'Got {1}.'.format(name, schedule_group.name))
        for schedule_group_name in self.schedule_groups:
            if schedule_group_name in self.membership_forms:
                raise ImproperlyConfigured('Visit Schedule Configuration attribute schedule_groups '
                                           'cannot have the same name as a membership_form. '
                                           'Got {0} in {1}.'.format(schedule_group_name,
                                                                    self.membership_forms.keys()))
        for schedule_group in self.schedule_groups.itervalues():
            if schedule_group.membership_form_name not in self.membership_forms:
                raise ImproperlyConfigured('Visit Schedule Configuration attribute schedule_groups '
                                           'refers to a membership_form not listed in attribute membership_forms. '
                                           'Got {0} not in {1}.'.format(schedule_group.membership_form_name,
                                                                        self.membership_forms.keys()))
        for visit_definition in self.visit_definitions.itervalues():
            for entry in visit_definition.get('entries'):
                if not get_model(entry.app_label, entry.model_name):
                    raise ImproperlyConfigured('Visit Schedule Configuration attribute entries refers '
                                               'to model {0}.{1} which does not exist.'.format(
                                                   entry.app_label, entry.model_name))
            for requisition_item in visit_definition.get('requisitions'):
                if not get_model(requisition_item.app_label, requisition_item.model_name):
                    raise ImproperlyConfigured('Visit Schedule Configuration attribute requisitions '
                                               'refers to model {0}.{1} which does not exist.'.format(
                                                   requisition_item.app_label, requisition_item.model_name))

    def sync_content_type_map(self):
        """Repopulates and syncs the ContentTypeMap instances."""
        content_type_map_helper = ContentTypeMapHelper()
        content_type_map_helper.populate()
        content_type_map_helper.sync()

    def rebuild(self):
        """Rebuild, WARNING which DELETES meta data."""
        Appointment = get_model('edc_appointment', 'appointment')
        Entry = get_model('entry', 'entry')
        MembershipForm = get_model('visit_schedule', 'membershipform')
        VisitDefinition = get_model('visit_schedule', 'visitdefinition')
        ScheduleGroup = get_model('visit_schedule', 'schedulegroup')
        self.verify()
        for code in self.visit_definitions.iterkeys():
            if VisitDefinition.objects.filter(code=code):
                obj = VisitDefinition.objects.get(code=code)
                Entry.objects.filter(visit_definition=obj).delete()
                if not Appointment.objects.filter(visit_definition=obj):
                    obj.delete()
        for schedule_group_name in self.schedule_groups.iterkeys():
            ScheduleGroup.objects.filter(group_name=schedule_group_name).delete()
        for membership_form_name in self.membership_forms.iterkeys():
            MembershipForm.objects.filter(category=membership_form_name).delete()
        self.build()

    def build(self):
        """Builds and / or updates the visit schedule models.

        If it hangs here then you are probably missing an app in INSTALLED_APPS."""
        entry_item = None
        Entry = get_model('entry', 'entry')
        RequisitionPanel = get_model('entry', 'requisitionpanel')
        LabEntry = get_model('entry', 'labentry')
        MembershipForm = get_model('visit_schedule', 'membershipform')
        VisitDefinition = get_model('visit_schedule', 'visitdefinition')
        ScheduleGroup = get_model('visit_schedule', 'schedulegroup')
        self.verify()
        while True:
            try:
                for membership_form in self.membership_forms.itervalues():
                    try:
                        obj = MembershipForm.objects.get(category=membership_form.name)
                        obj.app_label = membership_form.model._meta.app_label
                        obj.model_name = membership_form.model._meta.object_name
                        obj.content_type_map = ContentTypeMap.objects.get(
                            app_label=membership_form.model._meta.app_label,
                            module_name=membership_form.model._meta.object_name.lower())
                        obj.visible = membership_form.visible
                        obj.save()
                    except MembershipForm.DoesNotExist:
                        MembershipForm.objects.filter(
                            content_type_map=ContentTypeMap.objects.get(
                                app_label=membership_form.model._meta.app_label,
                                module_name=membership_form.model._meta.object_name.lower())).delete()
                        MembershipForm.objects.create(
                            category=membership_form.name,
                            app_label=membership_form.model._meta.app_label,
                            model_name=membership_form.model._meta.object_name,
                            content_type_map=ContentTypeMap.objects.get(
                                app_label=membership_form.model._meta.app_label,
                                module_name=membership_form.model._meta.object_name.lower()),
                            visible=membership_form.visible)
                for group_name, schedule_group in self.schedule_groups.iteritems():
                    try:
                        obj = ScheduleGroup.objects.get(group_name=group_name)
                        obj.group_name = group_name
                        obj.membership_form = MembershipForm.objects.get(category=schedule_group.membership_form_name)
                        obj.grouping_key = schedule_group.grouping_key
                        obj.comment = schedule_group.comment
                        obj.save()
                    except ScheduleGroup.DoesNotExist:
                        ScheduleGroup.objects.create(
                            group_name=group_name,
                            membership_form=MembershipForm.objects.get(category=schedule_group.membership_form_name),
                            grouping_key=schedule_group.grouping_key,
                            comment=schedule_group.comment)
                for code, visit_definition in self.visit_definitions.iteritems():
                    visit_tracking_content_type_map = ContentTypeMap.objects.get(
                        app_label=visit_definition.get('visit_tracking_model')._meta.app_label,
                        module_name=visit_definition.get('visit_tracking_model')._meta.object_name.lower())
                    schedule_group = ScheduleGroup.objects.get(group_name=visit_definition.get('schedule_group'))
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
                        visit_definition_instance.schedule_group.add(schedule_group)
                    for entry_item in visit_definition.get('entries'):
                        content_type_map = ContentTypeMap.objects.get(
                            app_label=entry_item.app_label, module_name=entry_item.model_name.lower())
                        try:
                            entry = Entry.objects.get(
                                app_label=entry_item.app_label,
                                model_name=entry_item.model_name.lower(),
                                visit_definition=visit_definition_instance)
                            entry.entry_order = entry_item.order
                            entry.default_entry_status = entry_item.default_entry_status
                            entry.additional = entry_item.additional
                            entry.save(update_fields=['entry_order', 'default_entry_status', 'additional'])
                        except Entry.DoesNotExist:
                            Entry.objects.create(
                                content_type_map=content_type_map,
                                visit_definition=visit_definition_instance,
                                entry_order=entry_item.order,
                                app_label=entry_item.app_label.lower(),
                                model_name=entry_item.model_name.lower(),
                                default_entry_status=entry_item.default_entry_status,
                                additional=entry_item.additional)
                    for entry in Entry.objects.filter(visit_definition=visit_definition_instance):
                        model_tpls = []
                        for item in visit_definition.get('entries'):
                            model_tpls.append((item.app_label.lower(), item.model_name.lower()))
                        if (entry.app_label.lower(), entry.model_name.lower()) not in model_tpls:
                            pass
                    for requisition_item in visit_definition.get('requisitions'):
                        # requisition panel must exist, see app_configuration
                        try:
                            requisition_panel = RequisitionPanel.objects.get(
                                name=requisition_item.requisition_panel_name)
                        except RequisitionPanel.DoesNotExist:
                            raise AppConfigurationError(
                                'RequisitionPanel matching query does not exist, '
                                'for name=\'{}\'. Re-run app_configuration.'
                                'prepare() or check the config.'.format(requisition_item.requisition_panel_name))
                        try:
                            lab_entry = LabEntry.objects.get(
                                requisition_panel=requisition_panel,
                                visit_definition=visit_definition_instance)
                            lab_entry.app_label = requisition_item.app_label
                            lab_entry.model_name = requisition_item.model_name
                            lab_entry.entry_order = requisition_item.entry_order
                            lab_entry.default_entry_status = requisition_item.default_entry_status
                            lab_entry.additional = requisition_item.additional
                            lab_entry.save(update_fields=[
                                'app_label', 'model_name', 'entry_order', 'default_entry_status', 'additional'])
                        except LabEntry.DoesNotExist:
                            try:
                                LabEntry.objects.create(
                                    app_label=requisition_item.app_label,
                                    model_name=requisition_item.model_name,
                                    requisition_panel=requisition_panel,
                                    visit_definition=visit_definition_instance,
                                    entry_order=requisition_item.entry_order,
                                    default_entry_status=requisition_item.default_entry_status,
                                    additional=requisition_item.additional)
                            except IntegrityError:
                                raise IntegrityError(
                                    '{} {} {}.{}'.format(
                                        visit_definition_instance, requisition_panel,
                                        requisition_item.app_label, requisition_item.model_name,))
                    for lab_entry in LabEntry.objects.filter(visit_definition=visit_definition_instance):
                        model_tpls = [
                            (item.app_label, item.model_name) for item in visit_definition.get('requisitions')]
                        if (lab_entry.app_label, lab_entry.model_name) not in model_tpls:
                            lab_entry.delete()
            except ContentTypeMap.DoesNotExist as e:
                if self.sync_content_type_map_tries == 0:
                    self.sync_content_type_map()
                    self.sync_content_type_map_tries += 1
                    continue
                else:
                    raise ContentTypeMap.DoesNotExist(
                        '{} Check INSTALLED_APPS for an APP '
                        'that is referenced but not installed. e.g. edc_offstudy.'.format(str(e)))
            break
