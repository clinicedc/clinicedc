from collections import OrderedDict, namedtuple

from django.core.exceptions import ImproperlyConfigured
from django.apps import apps
from django.db.utils import IntegrityError

from edc_content_type_map.classes import ContentTypeMapHelper
from edc_content_type_map.models import ContentTypeMap

EntryTuple = namedtuple('EntryTuple', 'order app_label model_name default_entry_status additional')
MemberTuple = namedtuple('MemberTuple', 'name model visible')
RequisitionPanelTuple = namedtuple('RequisitionPanelTuple', 'entry_order app_label model_name '
                                   'requisition_panel_name panel_type aliquot_type_alpha_code '
                                   'default_entry_status additional')
ScheduleGroupTuple = namedtuple('ScheduleTuple', 'name member_name grouping_key comment')


class VisitScheduleConfiguration(object):
    """Creates or updates the member, schedule_group, entry,
    lab_entry models and visit_definition.

        .. note:: RequisitionPanel is needed for lab_entry but is
                 populated in the app_configuration and not here."""

    name = 'unnamed visit schedule'
    app_label = None
    members = OrderedDict()
    schedule_groups = OrderedDict()
    visit_definitions = OrderedDict()

    def __init__(self):
        self.appointment_cls = apps.get_model('appointment', 'appointment')
        self.entry_cls = apps.get_model('entry', 'entry')
        self.member_cls = apps.get_model('edc_visit_schedule', 'member')
        self.visit_definition_cls = apps.get_model('edc_visit_schedule', 'visitdefinition')
        self.scheduleGroup_cls = apps.get_model('edc_visit_schedule', 'schedulegroup')
        self.requisition_panel_cls = apps.get_model('entry', 'requisitionpanel')
        self.lab_entry_cls = apps.get_model('entry', 'labentry')

    def __repr__(self):
        return '{0}.{1}'.format(self.app_label, self.name)

    def verify(self):
        """Verifies some aspects of the the format of the dictionary attributes."""
        for name, member in self.members.items():
            if not name == member.name:
                raise ImproperlyConfigured(
                    'Visit Schedule Configuration attribute members '
                    'expects each dictionary key {0} to be in it\'s named tuple. '
                    'Got {1}.'.format(name, member.name))
        for schedule_group in self.schedule_groups.values():
            if not issubclass(schedule_group.__class__, ScheduleGroupTuple):
                raise ImproperlyConfigured('Visit Schedule Configuration attribute schedule_groups '
                                           'must contain instances of the named tuple ScheduleGroupTuple. '
                                           'Got {0}'.format(schedule_group))
        for name, schedule_group in self.schedule_groups.items():
            if not name == schedule_group.name:
                raise ImproperlyConfigured('Visit Schedule Configuration attribute schedule_groups '
                                           'expects each dictionary key {0} to be in it\'s named tuple. '
                                           'Got {1}.'.format(name, schedule_group.name))
        for schedule_group_name in self.schedule_groups:
            if schedule_group_name in self.members:
                raise ImproperlyConfigured('Visit Schedule Configuration attribute schedule_groups '
                                           'cannot have the same name as a member. '
                                           'Got {0} in {1}.'.format(schedule_group_name,
                                                                    self.members))
        for schedule_group in self.schedule_groups.values():
            if schedule_group.member_name not in self.members:
                raise ImproperlyConfigured('Visit Schedule Configuration attribute schedule_groups '
                                           'refers to a member not listed in attribute members. '
                                           'Got {0} not in {1}.'.format(schedule_group.member_name,
                                                                        self.members))
        for visit_definition in self.visit_definitions.values():
            for entry in visit_definition.get('entries'):
                try:
                    apps.get_model(entry.app_label, entry.model_name)
                except LookupError:
                    raise ImproperlyConfigured(
                        'Visit Schedule Configuration attribute entries refers '
                        'to model {0}.{1} which does not exist.'.format(
                            entry.app_label, entry.model_name))
            for requisition_item in visit_definition.get('requisitions'):
                try:
                    apps.get_model(requisition_item.app_label, requisition_item.model_name)
                except LookupError:
                    raise ImproperlyConfigured(
                        'Visit Schedule Configuration attribute requisitions '
                        'refers to model {0}.{1} which does not exist.'.format(
                            requisition_item.app_label, requisition_item.model_name))

    def sync_content_type_map(self):
        """Repopulates and syncs the ContentTypeMap instances."""
        content_type_map_helper = ContentTypeMapHelper()
        content_type_map_helper.populate()
        content_type_map_helper.sync()

    def rebuild(self):
        """Rebuild, WARNING which DELETES meta data."""
        self.verify()
        for code in self.visit_definitions.iterkeys():
            if self.visit_definition_cls.objects.filter(code=code):
                obj = self.visit_definition_cls.objects.get(code=code)
                self.entry_cls.objects.filter(visit_definition=obj).delete()
                if not self.appointment_cls.objects.filter(visit_definition=obj):
                    obj.delete()
        for schedule_group_name in self.schedule_groups.iterkeys():
            self.scheduleGroup_cls.objects.filter(group_name=schedule_group_name).delete()
        for member_name in self.members.iterkeys():
            self.member_cls.objects.filter(category=member_name).delete()
        self.build()

    def build(self):
        """Builds and / or updates the visit schedule models."""
        self.verify()
        while True:
            try:
                self.update_members()
                self.update_schedule_groups()
                self.update_visit_definitions()
            except ContentTypeMap.DoesNotExist:
                self.sync_content_type_map()
                continue
            break

    def update_members(self):
        for member in self.members.values():
            try:
                obj = self.member_cls.objects.get(category=member.name)
                obj.app_label = member.model._meta.app_label
                obj.model_name = member.model._meta.object_name
                obj.content_type_map = ContentTypeMap.objects.get(
                    app_label=member.model._meta.app_label,
                    module_name=member.model._meta.object_name.lower())
                obj.visible = member.visible
                obj.save()
            except self.member_cls.DoesNotExist:
                self.member_cls.objects.filter(
                    content_type_map=ContentTypeMap.objects.get(
                        app_label=member.model._meta.app_label,
                        module_name=member.model._meta.object_name.lower())).delete()
                self.member_cls.objects.create(
                    category=member.name,
                    app_label=member.model._meta.app_label,
                    model_name=member.model._meta.object_name,
                    content_type_map=ContentTypeMap.objects.get(
                        app_label=member.model._meta.app_label,
                        module_name=member.model._meta.object_name.lower()),
                    visible=member.visible)

    def update_schedule_groups(self):
        for group_name, schedule_group in self.schedule_groups.items():
            try:
                obj = self.scheduleGroup_cls.objects.get(group_name=group_name)
                obj.group_name = group_name
                obj.member = self.member_cls.objects.get(category=schedule_group.member_name)
                obj.grouping_key = schedule_group.grouping_key
                obj.comment = schedule_group.comment
                obj.save()
            except self.scheduleGroup_cls.DoesNotExist:
                self.scheduleGroup_cls.objects.create(
                    group_name=group_name,
                    member=self.member_cls.objects.get(category=schedule_group.member_name),
                    grouping_key=schedule_group.grouping_key,
                    comment=schedule_group.comment)

    def update_visit_definitions(self):
        for code, visit_definition in self.visit_definitions.items():
            visit_tracking_content_type_map = ContentTypeMap.objects.get(
                app_label=visit_definition.get('visit_tracking_model')._meta.app_label,
                module_name=visit_definition.get('visit_tracking_model')._meta.object_name.lower())
            schedule_group = self.scheduleGroup_cls.objects.get(group_name=visit_definition.get('schedule_group'))
            try:
                visit_definition_instance = self.visit_definition_cls.objects.get(code=code)
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
            except self.visit_definition_cls.DoesNotExist:
                visit_definition_instance = self.visit_definition_cls.objects.create(
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
                    instruction=visit_definition.get('instructions') or '-',
                )
            finally:
                visit_definition_instance.schedule_group.add(schedule_group)

            self.update_entries(visit_definition, visit_definition_instance)

            self.delete_unused_entries(visit_definition, visit_definition_instance)

            self.update_requisitions(visit_definition, visit_definition_instance)

            self.update_lab_entries(visit_definition, visit_definition_instance)

    def update_entries(self, visit_definition, visit_definition_instance):
        for entry_item in visit_definition.get('entries'):
            content_type_map = ContentTypeMap.objects.get(
                app_label=entry_item.app_label, module_name=entry_item.model_name.lower())
            try:
                entry = self.entry_cls.objects.get(
                    app_label=entry_item.app_label,
                    model_name=entry_item.model_name.lower(),
                    visit_definition=visit_definition_instance)
                entry.entry_order = entry_item.order
                entry.default_entry_status = entry_item.default_entry_status
                entry.additional = entry_item.additional
                entry.save(update_fields=['entry_order', 'default_entry_status', 'additional'])
            except self.entry_cls.DoesNotExist:
                self.entry_cls.objects.create(
                    content_type_map=content_type_map,
                    visit_definition=visit_definition_instance,
                    entry_order=entry_item.order,
                    app_label=entry_item.app_label.lower(),
                    model_name=entry_item.model_name.lower(),
                    default_entry_status=entry_item.default_entry_status,
                    additional=entry_item.additional)

    def update_requisitions(self, visit_definition, visit_definition_instance):
        for requisition_item in visit_definition.get('requisitions'):
            # requisition panel must exist, see app_configuration
            try:
                requisition_panel = self.requisition_panel_cls.objects.get(
                    name=requisition_item.requisition_panel_name)
            except self.requisition_panel_cls.DoesNotExist:
                raise self.requisition_panel_cls.DoesNotExist(
                    'RequisitionPanel matching query does not exist, '
                    'for name=\'{}\'. Re-run app_configuration.'
                    'prepare() or check the config.'.format(requisition_item.requisition_panel_name))
            try:
                lab_entry = self.lab_entry_cls.objects.get(
                    requisition_panel=requisition_panel,
                    visit_definition=visit_definition_instance)
                lab_entry.app_label = requisition_item.app_label
                lab_entry.model_name = requisition_item.model_name
                lab_entry.entry_order = requisition_item.entry_order
                lab_entry.default_entry_status = requisition_item.default_entry_status
                lab_entry.additional = requisition_item.additional
                lab_entry.save(update_fields=[
                    'app_label', 'model_name', 'entry_order', 'default_entry_status', 'additional'])
            except self.lab_entry_cls.DoesNotExist:
                try:
                    self.lab_entry_cls.objects.create(
                        app_label=requisition_item.app_label,
                        model_name=requisition_item.model_name,
                        requisition_panel=requisition_panel,
                        visit_definition=visit_definition_instance,
                        entry_order=requisition_item.entry_order,
                        default_entry_status=requisition_item.default_entry_status,
                        additional=requisition_item.additional
                    )
                except IntegrityError:
                    raise IntegrityError(
                        '{} {} {}.{}'.format(
                            visit_definition_instance, requisition_panel,
                            requisition_item.app_label, requisition_item.model_name,))

    def update_lab_entries(self, visit_definition, visit_definition_instance):
        for lab_entry in self.lab_entry_cls.objects.filter(visit_definition=visit_definition_instance):
            if ((lab_entry.app_label, lab_entry.model_name) not in
                    [(item.app_label, item.model_name) for item in visit_definition.get('requisitions')]):
                lab_entry.delete()

    def delete_unused_entries(self, visit_definition, visit_definition_instance):
        """Deletes unused entries in the visit definition model."""
        items = []
        for item in visit_definition.get('entries'):
            items.append((item.app_label.lower(), item.model_name.lower()))
        for entry in self.entry_cls.objects.filter(visit_definition=visit_definition_instance):
            if (entry.app_label.lower(), entry.model_name.lower()) not in items:
                entry.delete()
