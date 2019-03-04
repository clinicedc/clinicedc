import re


class CleanSearchTermViewMixin:

    search_term_pattern = None

    def clean_search_term(self):
        search_term = super().clean_search_term()
        if search_term:
            search_terms = search_term.split("+")
            for index, term in enumerate(search_terms):
                if re.match(self.search_term_pattern, term):
                    search_terms[index] = "".join(term.split("_"))
            search_term = "+".join(search_terms)
        return search_term
