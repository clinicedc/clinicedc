from django import forms


class SearchForm(forms.Form):
    search_term = forms.CharField(
        max_length=30,
        label="",
        help_text="enter all or part of a word, name, identifier, etc",
        error_messages={'required': 'Please enter a search term.'},
        widget=forms.TextInput(attrs={'size': '10'})
    )
