from tempfile import mkstemp

from django.test import TestCase

from ...form_describer import FormDescriber
from ..admin import MyModelAdmin
from ..models import MyModel


class TestForDescribter(TestCase):
    def test_ok(self):
        describer = FormDescriber(admin_cls=MyModelAdmin, include_hidden_fields=True)
        txt = " ".join(describer.markdown)
        for f in MyModel._meta.get_fields():
            self.assertIn(f.verbose_name, txt)

    def test_to_file(self):
        tmp, name = mkstemp()
        describer = FormDescriber(admin_cls=MyModelAdmin, include_hidden_fields=True)
        describer.to_file(path=name, overwrite=True)
        with open(name, "r") as describer_file:
            txt = describer_file.read()
            for f in MyModel._meta.get_fields():
                self.assertIn(f.verbose_name, txt)
