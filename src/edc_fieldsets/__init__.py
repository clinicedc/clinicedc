from importlib.metadata import version

__version__ = version("edc_fieldsets")

from .fieldlist import Fieldlist, Insert, Remove
from .fieldset import Fieldset
from .fieldsets import FieldsetError, Fieldsets
from .fieldsets_modeladmin_mixin import FieldsetsModelAdminMixin
