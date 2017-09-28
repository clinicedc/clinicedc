from datetime import datetime
from edc_base.model_mixins.constants import DEFAULT_BASE_FIELDS
from math import floor


class FormDescriber:

    """A class that prepares form reference information in
    markdown text.

    Usage:
        describer = FormDescriber(
                admin_cls=MyModelAdmin,
                include_hidden_fields=True)
        markdown = describer.to_markdown(title='Forms', add_timestamp=True)
    """

    def __init__(self, admin_cls=None, include_hidden_fields=None):
        self.markdown = []
        self.admin_cls = admin_cls
        self.model_cls = admin_cls.form._meta.model
        self.models_fields = {
            fld.name: fld for fld in self.model_cls._meta.get_fields()}
        self.describe()
        if include_hidden_fields:
            self.add_hidden_fields()

    def describe(self):
        """Appends all form features to a list `lines`.
        """
        number = 0.0
        self.markdown.append(f'## {self.model_cls._meta.verbose_name}')
        self.markdown.append(self.model_cls.__doc__)
        self.markdown.append(
            f'*Instructions*: {self.admin_cls.instructions}\n')
        self.markdown.append(
            f'*Additional instructions*: {self.admin_cls.additional_instructions}\n')

        for fieldset_name, fields in self.admin_cls.fieldsets:
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
