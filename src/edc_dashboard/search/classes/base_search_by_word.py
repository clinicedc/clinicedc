import string

from django.db.models import Q

from edc_consent.models import BaseConsent

from .base_searcher import BaseSearcher


class BaseSearchByWord(BaseSearcher):

    @property
    def _qset(self):
        """Returns a Q() object, a tuple of Q() objects or None for the search result query.

        First tries the qset property, if it returns nothing, then
        tries the default methods for getting a Q() object.
        """
        qset = self.qset
        if not qset:
            if self.qset_by_keyword:
                qset = self.qset_by_keyword
            elif self.qset_by_search_term_pattern:
                qset = self.qset_by_search_term_pattern
            elif 'registered_subject' in dir(self.search_model()):
                qset = self.qset_for_registered_subject
            elif issubclass(self.search_model, BaseConsent):
                qset = self.qset_for_consent
            else:
                qset = self.default_qset
        return qset

    @property
    def qset(self):
        """Returns a qset for the search result query from the child class or none.

        Hint: use q.add(Q(), Q.OR) and add to an exiting q.

        For example::
            @property
            def qset(self):
                qset = self.qset_for_registered_subject
                qset.add(Q(household_structure__household__household_identifier__icontains=self.search_value), Q.OR)
            return qset
        """
        return None

    @property
    def search_result(self):
        """Returns a queryset using the search term as a filter.

        Values need from the request object or kwargs should be intercepted in the
        view method."""
        search_result = []
        form = self.search_form(self.search_form_data)
        if form.is_valid():
            self.search_value = form.data.get(self.search_form_field_name)
            if self.search_value[0] == '?':
                search_result = self.special_keyword_queryset
            else:
                try:
                    qset_filter, qset_exclude = self._qset
                except (ValueError, TypeError):
                    qset_filter = self.qset
                    qset_exclude = None
                if qset_filter and qset_exclude:
                    search_result = self.search_model.objects.filter(
                        qset_filter).exclude(qset_exclude).order_by(*self.order_by)
                elif qset_filter and not qset_exclude:
                    search_result = self.search_model.objects.filter(
                        qset_filter).order_by(*self.order_by)
                elif not qset_filter and qset_exclude:
                    search_result = self.search_model.objects.exclude(
                        qset_exclude).order_by(*self.order_by)
                else:
                    pass
        return search_result

    @property
    def default_qset(self):
        return self.qset

    @property
    def keyword_list(self):
        return []

    @property
    def display_keyword_list(self):
        return self.keyword_list

    @property
    def filter_keyword_url_list(self):
        return []

    @property
    def qset_by_search_term_pattern(self):
        """Returns a tuple of qsets, (filter, exclude), if the
        search value matches a given pattern, otherwise None."""
        return None

    @property
    def qset_for_registered_subject(self):
        self.order_by = ['registered_subject__subject_identifier', 'registered_subject__initials']
        qset = (
            Q(registered_subject__first_name__exact=self.search_value) |
            Q(registered_subject__last_name__exact=self.search_value) |
            Q(registered_subject__identity__exact=self.search_value) |
            Q(registered_subject__subject_identifier__icontains=self.search_value) |
            Q(registered_subject__initials__icontains=self.search_value) |
            Q(user_created__icontains=self.search_value) |
            Q(user_modified__icontains=self.search_value)
        )
        return qset

    @property
    def qset_for_consent(self):
        self.order_by = ['subject_identifier']
        qset = (
            Q(subject_identifier__icontains=self.search_value) |
            Q(first_name__exact=self.search_value) |
            Q(last_name__exact=self.search_value) |
            Q(identity__exact=self.search_value) |
            Q(initials__icontains=self.search_value) |
            Q(user_created__icontains=self.search_value) |
            Q(user_modified__icontains=self.search_value)
            )
        return qset

    @property
    def qset_by_keyword(self):
        """Returns a qset based on matching keyword.

        If you predefine keywords, the search term will be intercepted and
        used to select a query instead.

        Search terms prefixed by '-' imply an exclusion (NOT <search_term>)."""
        qset_filter = Q()
        qset_exclude = Q()
        if (self.search_value.lower() in map(string.lower, self.keyword_list) +
                ['-{0}'.format(item) for item in map(string.lower, self.keyword_list)]):
            if self.search_value[0] == '-':
                search_value = [item for item in map(string.lower, self.keyword_list)
                                if item == self.search_value[1:]][0]
                qset_exclude = Q(member_status=search_value)
            else:
                search_value = [item for item in map(string.lower, self.keyword_list)
                                if item == self.search_value.lower()][0]
                qset_filter = Q(member_status=search_value)
        if qset_filter or qset_exclude:
            return (qset_filter, qset_exclude)
        return None
