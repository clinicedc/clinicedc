from django.core.exceptions import FieldError


class PackingListHelper(object):
    """A class to handle the packing list.

    Depends on the properties declared on the packing list model:
        * item_models: a list of Model classes that can be added to the
            packing list. So far handles Aliquot (expects field attr
            \'aliquot_identifier\' and a base class of Requisition
            (expects \'specimen_identifier\').
        * packing_list_item_model: returns model class for the
            packing_list_item (related to PackingList)
    Depends on property or attribute on the item model (e.g. Requisition, Aliquot):
        * registered_subject
        * visit_code

        For example on Aliquot::
            @property
            def registered_subject(self):
                return self.receive.registered_subject

            @property
            def visit_code(self):
                return self.receive.visit

    """

    def __init__(self, packing_list, user=None):
        self.packing_list = packing_list
        self.user = user

    def __repr__(self):
        return 'PackingListHelper({0.packing_list})'.format(self)

    def __str__(self):
        return 'PackingListHelper({0.packing_list})'.format(self)

    def update(self):
        """Called on packing_list post_save signal"""
        # convert the text list of item identifiers into a list of parsed identifiers
        item_identifiers = filter(None, self.packing_list.list_items.replace('\r', '').split('\n'))
        # loop through list of parsed identifiers
        for item_identifier in item_identifiers:
            # 1. get the 'item' instance for this identifier and update it (e.g. SubjectRequisition, Aliquot)
            # 2. create a 'packing_list_item' instance related to this packing_list
            for item_model in self.packing_list.item_models:
                try:
                    try:
                        item = item_model.objects.get(specimen_identifier=item_identifier)
                        optional_attrs = {'panel': item.panel, 'item_priority': item.priority}
                    except FieldError:
                        item = item_model.objects.get(aliquot_identifier=item_identifier)
                        optional_attrs = {}
                    user = self.user or item.user_modified
                    self._update_item(item, user)
                    self._create_or_update_packinglistitem(
                        item_identifier,
                        item,
                        user,
                        optional_attrs=optional_attrs)
                except item_model.DoesNotExist:
                    pass

    def _update_item(self, item, user):
        """Updates the item (requisition or aliquot) to indicate that it is packed."""
        item.user_modified = user
        try:
            item.panel = item.panel
            item.item_priority = item.priority
        except AttributeError:
            pass
        item.is_packed = True
        item.save()
        return item

    def _create_or_update_packinglistitem(self, item_identifier, item, user, optional_attrs={}):
        """Creates or updates the packing list item for this "item"."""
        try:
            packing_list_item = self.packing_list.packing_list_item_model.objects.get(
                packing_list=self.packing_list,
                item_reference=item_identifier)
        except self.packing_list.packing_list_item_model.DoesNotExist:
            try:
                optional_description = item.optional_description or ''
            except AttributeError:
                optional_description = None
            options = {
                'requisition': item._meta.verbose_name,
                'item_description': '{subject_identifier} ({initials}) VISIT:{visit} DOB:{dob} {optional}'.format(
                    subject_identifier=item.registered_subject.subject_identifier,
                    initials=item.registered_subject.initials,
                    visit=item.visit_code,
                    dob=item.registered_subject.dob,
                    optional=optional_description,
                    ),
                'user_created': user,
                }
            options.update(**optional_attrs)
            packing_list_item = self.packing_list.packing_list_item_model.objects.create(
                packing_list=self.packing_list,
                item_reference=item_identifier,
                **options)
        return packing_list_item
