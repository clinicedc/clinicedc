from django.db.models import get_model


class VisitDefinitionHelper(object):

    def copy(self, source_visit_definition, code, title, time_point, base_interval, base_interval_unit, grouping=None):
        VisitDefinition = get_model('edc_visit_schedule', 'VisitDefinition')
        Entry = get_model('entry', 'Entry')

        target_visit_definition = VisitDefinition.objects.create(
            code=code,
            title=title,
            grouping=grouping,
            time_point=time_point,
            base_interval=base_interval,
            base_interval_unit=base_interval_unit)
        #for schedule_group in source_visit_definition.schedule_group.all():
        #    target_visit_definition.schedule_group.add(schedule_group)
        for entry in Entry.objects.filter(visit_definition=source_visit_definition):
            options = {}
            entry.visit_definition = target_visit_definition
            for fld in entry._meta.fields:
                if fld.name not in ['id', 'created', 'modified', 'user_created', 'user_modified', 'hostname_created', 'hostname_modified']:
                    options.update({fld.name: getattr(entry, fld.name)})
            Entry.objects.create(**options)
