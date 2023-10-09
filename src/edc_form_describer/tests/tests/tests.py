from tempfile import mkstemp

from django.test import TestCase

from ...form_describer import FormDescriber
from ..admin import MyModelAdmin
from ..models import MyModel


class TestForDescribter(TestCase):
    @staticmethod
    def get_fields_from_fieldset(admin_cls) -> list[str]:
        fields = []
        for _, fields_dict in admin_cls.fieldsets:
            for f in fields_dict["fields"]:
                fields.append(f)
        return fields

    def test_ok(self):
        describer = FormDescriber(admin_cls=MyModelAdmin, include_hidden_fields=True)
        txt = " ".join(describer.markdown)
        fields = self.get_fields_from_fieldset(MyModelAdmin)
        for f in MyModel._meta.get_fields():
            if f.name in fields:
                self.assertIn(str(f.verbose_name), txt)

    def test_to_file(self):
        tmp, name = mkstemp()
        describer = FormDescriber(admin_cls=MyModelAdmin, include_hidden_fields=True)
        describer.to_file(path=name, overwrite=True)
        with open(name, "r") as describer_file:
            txt = describer_file.read()
            fields = self.get_fields_from_fieldset(MyModelAdmin)
            for f in MyModel._meta.get_fields():
                if f.name in fields:
                    self.assertIn(str(f.verbose_name), txt)
