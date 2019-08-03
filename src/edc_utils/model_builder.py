"""
fields = []
for field_name, data in txt.items():
    fields.append(FieldBuilder(field_name, data))
for f in fields:
    f.print_choices()
for f in fields:
    f.print_fields()
"""


class ModelBuilder:
    def __init__(self, model_name, verbose_name, verbose_name_plural):
        self.field_builders = {}
        self.tab = "    "
        self.model_name = model_name
        self.verbose_name = verbose_name
        self.verbose_name_plural = verbose_name_plural

    def add(self, data):
        for field_name, string_data in data.items():
            self.add_field(field_name, string_data)

    def add_field(self, field_name, txt):
        fb = FieldBuilder(field_name, txt)
        self.field_builders.update({field_name: fb})

    def p(self):
        for _, fb in self.field_builders.items():
            fb.print_choices()
        print(f"class {self.model_name}(CrfModelMixin, BaseUuidModel):")
        for _, fb in self.field_builders.items():
            fb.print_fields()
        print(f"{self.tab}class Meta:")
        print(f'{self.tab}{self.tab}verbose_name="{self.verbose_name}"')
        print(f'{self.tab}{self.tab}verbose_name_plural="{self.verbose_name_plural}"')

    def field_list(self):
        return list(self.field_builders.keys())


class FieldBuilder:
    def __init__(self, field_name, txt):

        self.tab = "    "
        txt = txt.strip()
        try:
            txt, self.help_text = txt.split("help_text=")
        except ValueError:
            self.help_text = None
        self.data = [y.strip() for y in txt.split("\n") if y]
        self.data = [y.strip() for y in txt.split("\n") if y]
        self.field_name = field_name or "field_name"
        self.verbose_name = self.data[0].strip()
        self.choices = []
        for item in self.data[1:]:
            item = item.strip()
            choice = (
                item.split("=")[1].strip().replace(" ", "_").replace("-", "_").lower()
            )
            self.choices.append((choice, item.split("=")[1].strip()))
        self.choices = tuple(self.choices)
        self.max_length = max([len(x[1]) for x in self.choices])
        if self.max_length < 15:
            self.max_length = 15
        self.choices_name = f"{self.field_name.upper()}_CHOICES"

    @property
    def choices_output(self):
        output = [f"{self.choices_name} = ("]
        for choice in self.choices:
            output.append(f'{self.tab}("{choice[0]}", "{choice[1]}"),')
        output.append(f")")
        return output

    @property
    def field_output(self):
        output = [f"{self.tab}{self.field_name} = models.CharField("]
        output.append(f'{self.tab}{self.tab}verbose_name="{self.verbose_name}",')
        output.append(f"{self.tab}{self.tab}max_length={self.max_length},")
        output.append(f"{self.tab}{self.tab}choices={self.choices_name},")
        if self.help_text:
            output.append(f'{self.tab}{self.tab}help_text="{self.help_text.strip()}",')
        output.append(f"{self.tab})\n")
        return output

    def field_names(self):
        return

    def print_choices(self):
        print("\n".join(self.choices_output))

    def print_fields(self):
        print("\n".join(self.field_output))
