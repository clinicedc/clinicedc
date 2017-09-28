from datetime import datetime
from edc_base.fieldsets.fieldsets import Fieldsets
from edc_base.model_mixins.constants import DEFAULT_BASE_FIELDS
from math import floor


class FormDescriber:

    """A class that prepares form reference information in
    markdown text.

    Usage:
        describer = FormDescriber(
                admin_cls=MyModelAdmin,
                include_hidden_fields=True)

        # get the markdown text as a list of lines
        markdown_lines = describer.markdown

        # get the markdown as text
        markdown = describer.to_markdown(title='Forms', add_timestamp=True)

        # or write markdown text directly to file
        describer.to_file(path=path, title='Forms', add_timestamp=True)

    """

    def __init__(self, admin_cls=None, include_hidden_fields=None, visit_code=None):
        self.markdown = []
        self.admin_cls = admin_cls
        self.model_cls = admin_cls.form._meta.model
        self.visit_code = visit_code
        self.models_fields = {
            fld.name: fld for fld in self.model_cls._meta.get_fields()}

        # include custom labels from admin
        self.custom_form_labels = {k: v for k, v in [
            (form_label.field, form_label.label)
            for form_label in self.admin_cls.custom_form_labels]}

        # include custom fieldsets from admin if visit_code
        self.fieldsets = self.admin_cls.fieldsets
        if self.admin_cls.conditional_fieldsets.get(self.visit_code):
            self.conditional_fieldset = self.admin_cls.conditional_fieldsets.get(
                self.visit_code)
            fieldsets = Fieldsets(self.admin_cls.fieldsets)
            fieldsets.add_fieldset(fieldset=self.conditional_fieldset)
            self.fieldsets = fieldsets.fieldsets

        self.describe()
        if include_hidden_fields:
            self.add_hidden_fields()

    def describe(self):
        """Appends all form features to a list `lines`.
        """
        number = 0.0
        verbose_name = self.model_cls._meta.verbose_name
        if self.visit_code and self.conditional_fieldset:
            verbose_name = f'{verbose_name} ({self.visit_code})'
        self.markdown.append(f'## {verbose_name}')
        docstring = self.model_cls.__doc__
        if docstring.lower().startswith(self.model_cls._meta.label_lower.split('.')[1]):
            self.markdown.append('*[missing model class docstring]*\n\n')
        else:
            self.markdown.append(self.model_cls.__doc__)
        self.markdown.append(
            f'*Instructions*: {self.admin_cls.instructions}\n')
        if self.admin_cls.additional_instructions:
            self.markdown.append(
                f'*Additional instructions*: {self.admin_cls.additional_instructions}\n')

        for fieldset_name, fields in self.fieldsets:
            if fieldset_name not in ['Audit']:
                fieldset_name = fieldset_name or 'Main'
                self.markdown.append(f'\n**Section: {fieldset_name}**')
                for fnames in fields.values():
                    for fname in fnames:
                        if fname not in DEFAULT_BASE_FIELDS:
                            number = self.get_next_number(number, fname)
                            self.add_field(fname=fname, number=number)

    def to_markdown(self, title=None, add_timestamp=None):
        """Returns the markdown text.
        """
        if title:
            self.markdown.insert(0, f'# {title}')
        if add_timestamp:
            timestamp = datetime.today().strftime('%Y-%m-%d %H:%M')
            self.markdown.insert(len(self.markdown) - 1,
                                 f'\n\n*Rendered on {timestamp}*\n')
        return '\n'.join(self.markdown)

    def to_file(self, path=None, title=None, add_timestamp=None):
        with open(path, 'w') as f:
            f.write(self.to_markdown(title=title, add_timestamp=add_timestamp))

    def add_foreign_keys(self):
        self.markdown.append(f'\n**Foreign keys:**')

    def add_m2ms(self):
        self.markdown.append(f'\n**Many2Many keys:**')

    def add_hidden_fields(self):
        self.markdown.append(f'\n**Hidden fields:**')
        self.add_field(fname='report_datetime')
        base_fields = DEFAULT_BASE_FIELDS
        base_fields.sort()
        for fname in base_fields:
            self.add_field(fname=fname)

    def add_field(self, fname=None, number=None):
        number = number or '@'
        field_cls = self.models_fields.get(fname)
        self.markdown.append(f'\n**{number}.** {field_cls.verbose_name}')
        if field_cls.help_text:
            self.markdown.append(
                f'\n&nbsp;&nbsp;&nbsp;&nbsp; *{field_cls.help_text}*')
        if self.custom_form_labels.get(fname):
            self.markdown.append(
                f'* custom_prompt: *{self.custom_form_labels.get(fname)}*')
        self.markdown.append(f'* db_table: {self.model_cls._meta.db_table}')
        self.markdown.append(f'* column: {field_cls.name}')
        self.markdown.append(f'* type: {field_cls.get_internal_type()}')
        if field_cls.max_length:
            self.markdown.append(f'* length: {field_cls.max_length}')
        if field_cls.get_internal_type() == 'DateField':
            self.markdown.append(f'* format: YYYY-MM-DD')
        if field_cls.get_internal_type() == 'DateTimeField':
            self.markdown.append(f'* format: YYYY-MM-DD HH:MM:SS.sss (tz=UTC)')
        self.add_field_responses(field_cls=field_cls)
        self.markdown.append('---')

    def add_field_responses(self, field_cls=None):
        if field_cls.get_internal_type() == 'CharField':
            if field_cls.choices:
                self.markdown.append(f'* responses:')
                for response in [f'`{tpl[0]}`: *{tpl[1]}*' for tpl in field_cls.choices]:
                    self.markdown.append(f'  - {response} ')
            else:
                self.markdown.append('* responses: *free text*')
        elif field_cls.get_internal_type() == 'ManyToManyField':
            self.markdown.append('* responses: *Select all that apply*')
            for obj in field_cls.related_model.objects.all().order_by('display_index'):
                self.markdown.append(f'  - `{obj.short_name}`: *{obj.name}* ')

    def get_next_number(self, number=None, fname=None):
        if '_other' in fname:
            number += 0.1
        else:
            number = floor(number)
            number += 1.0
        return number
