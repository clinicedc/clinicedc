from tempfile import mkstemp

from django.test import TestCase

from edc_form_describer.form_describer import FormDescriber
from tests.admin import TestModel3Admin
from tests.models import TestModel3


class TestForDescriber(TestCase):
    @staticmethod
    def get_fields_from_fieldset(admin_cls) -> list[str]:
        fields = []
        for _, fields_dict in admin_cls.fieldsets:
            for f in fields_dict["fields"]:
                fields.append(f)
        return fields

    def test_ok(self):
        describer = FormDescriber(admin_cls=TestModel3Admin, include_hidden_fields=True)
        txt = " ".join(describer.markdown)
        fields = self.get_fields_from_fieldset(TestModel3Admin)
        for f in TestModel3._meta.get_fields():
            if f.name in fields:
                self.assertIn(str(f.verbose_name), txt)

    def test_to_file(self):
        tmp, name = mkstemp()
        describer = FormDescriber(admin_cls=TestModel3Admin, include_hidden_fields=True)
        describer.to_file(path=name, overwrite=True)
        with open(name, "r") as describer_file:
            txt = describer_file.read()
            fields = self.get_fields_from_fieldset(TestModel3Admin)
            for f in TestModel3._meta.get_fields():
                if f.name in fields:
                    self.assertIn(str(f.verbose_name), txt)
