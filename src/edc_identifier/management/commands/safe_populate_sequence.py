from django.conf import settings

from django.core.management.base import BaseCommand

from ...models import Sequence, SubjectIdentifier


class Command(BaseCommand):

    help = ('Looks up highest sequence in SubjectIdentifiers '
            'and populates sequences up to that stage.')

    def handle(self, *args, **options):
        self.populate()

    def populate(self):
        identifiers = SubjectIdentifier.objects.all()
        identifier_sequences = []
        for identifier in identifiers:
            tokens = identifier.identifier.split('-')
            identifier_sequences.append(int(tokens[1][4:]))
        maxnum = identifier_sequences[0]
        for num in identifier_sequences:
            if num > max:
                maxnum = num
        maxnum += 1
        max_sequence = 0
        if Sequence.objects.all().exists():
            max_sequence = Sequence.objects.all().order_by('-id')[0].id
        if max > max_sequence:
            print('SubjectIdentifiers up to {}, Sequences up to {}'.format(max, max_sequence))
            for _ in range(max_sequence, max + 1):
                created = Sequence.objects.create(device_id=settings.DEVICE_ID)
                print('Created Sequence {} for DEVICE_ID={}'.format(created.id, settings.DEVICE_ID))
        else:
            print('Everything OK, did nothing')
