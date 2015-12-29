from datetime import datetime

from django.contrib.auth.models import User
from django.conf import settings

from edc_constants.constants import YES

from ..exceptions import SpecimenError


class LabProfile(object):

    name = None
    profile_group_name = None  # controller uses this to register the aliquot, receive, ... models so they can be referenced by the group name
    receive_model = None
    panel_model = None
    aliquot_model = None
    aliquot_type_model = None
    profile_model = None
    profile_item_model = None
    requisition_model = None

    def __init__(self):
        self.profile_group_name = self.requisition_model._meta.object_name

    def __repr__(self):
        return '({0.profile_group_name})'.format(self)

    def __str__(self):
        return '({0.profile_group_name})'.format(self)

    def receive(self, requisition):
        """Receives a specimen, creates the primary aliqout based on the requisition
        and updates the requisition as received."""
        receive = None
        if requisition.is_drawn == YES:
            try:
                receive = self.receive_model.objects.get(
                    receive_identifier=requisition.specimen_identifier)
            except self.receive_model.DoesNotExist:
                try:
                    # get phlebotomists initials
                    user = User.objects.get(username=requisition.user_created)
                    clinician_initials = '{0}{1}'.format(user.first_name[:1].upper(), user.last_name[:1].upper())
                except User.DoesNotExist:
                    clinician_initials = 'XX'
                # capture basic info on specimen
                requisition.is_receive = True
                requisition.is_receive_datetime = datetime.today()
                receive = self.receive_model.objects.create(
                    registered_subject=requisition.get_visit().appointment.registered_subject,
                    receive_identifier=self.specimen_identifier(requisition),
                    requisition_identifier=requisition.requisition_identifier,
                    requisition_model_name=requisition._meta.object_name,
                    drawn_datetime=requisition.drawn_datetime,
                    clinician_initials=clinician_initials,
                    visit=requisition.get_visit().appointment.visit_definition.code)
                # update requisition
                requisition.specimen_identifier = receive.receive_identifier
                requisition.save(update_fields=['is_receive', 'is_receive_datetime', 'specimen_identifier'])
            try:
                self.aliquot_model.objects.get(receive=receive)
            except self.aliquot_model.DoesNotExist:
                # create primary aliquot
                self.aliquot_model.objects.create(
                    aliquot_identifier=self.aliquot_identifier(receive, requisition.aliquot_type, 1),
                    primary_aliquot=None,
                    source_aliquot=None,
                    receive=receive,
                    count=0,
                    aliquot_type=requisition.aliquot_type,
                    aliquot_condition=None)
                # FIXME: BAD, this should be left as NONE for primary!!!!!!
                # aliquot.primary_aliquot = aliquot
                # aliquot.save()
        return receive

    def specimen_identifier(self, requisition):
        specimen_identifier = None
        if requisition.specimen_identifier:
            specimen_identifier = requisition.specimen_identifier
        else:
            if requisition.is_receive and requisition.is_drawn == YES:
                specimen_identifier = '{0}{1}{2}'.format(
                    settings.PROJECT_IDENTIFIER_PREFIX,
                    requisition.study_site,
                    requisition.requisition_identifier)
        if not specimen_identifier:
            raise SpecimenError('Cannot set specimen identifier for the specimen in Requisition {}. '
                                'Either specimen is not drawn or not flagged as received. Got {}{}.'.format(
                                    requisition, '' if requisition.is_drawn == YES else 'not drawn ',
                                    '' if requisition.is_receive else 'not received '))
        return specimen_identifier

    def aliquot(self, source_aliquot_or_pk, aliquot_type, count):
        """Creates aliquots from the source aliquot and increments the aliquot count from the existing primary."""
        try:
            source_aliquot = self.aliquot_model.objects.get(pk=source_aliquot_or_pk)
        except self.aliquot_model.DoesNotExist:
            source_aliquot = source_aliquot_or_pk
        aliquot_count = self.aliquot_model.objects.filter(receive=source_aliquot.receive).count()
        for _ in range(count):
            aliquot_count = aliquot_count + 1
            self.aliquot_model.objects.create(
                aliquot_identifier=self.aliquot_identifier(source_aliquot, aliquot_type, aliquot_count),
                primary_aliquot=source_aliquot.primary_aliquot,
                source_aliquot=source_aliquot,
                count=aliquot_count,
                receive=source_aliquot.receive,
                aliquot_type=aliquot_type,
                aliquot_condition=None)

    def aliquot_by_profile(self, source_aliquot, profile):
        """Create aliquots as per the profile."""
        for obj in self.profile_item_model.objects.filter(profile=profile):
            self.aliquot(source_aliquot, obj.aliquot_type, obj.count)

    def aliquot_identifier(self, source, aliquot_type, aliquot_count):
        """Returns an aliquot identifier create from a source aliquot or,
        if PRIMARY, from the receive identifier.

        Args:
            source: either an aliquot or receive instance."""
        aliquot_stub = '{0}{1}'.format(aliquot_type.numeric_code.zfill(2), str(aliquot_count).zfill(2))
        try:
            return '{0}{1}'.format(source.receive.receive_identifier, aliquot_stub)
        except AttributeError:
            return '{0}{1}'.format(source.receive_identifier, aliquot_stub)
