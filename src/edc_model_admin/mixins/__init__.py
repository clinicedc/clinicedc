from .address_model_admin_mixin import AddressModelAdminMixin
from .inlines import (
    LimitedAdminInlineMixin,
    StackedInlineModelAdminMixin,
    TabularInlineMixin,
)
from .model_admin_form_auto_number_mixin import ModelAdminFormAutoNumberMixin
from .model_admin_form_instructions_mixin import ModelAdminFormInstructionsMixin
from .model_admin_institution_mixin import ModelAdminInstitutionMixin
from .model_admin_model_redirect_mixin import ModelAdminModelRedirectMixin
from .model_admin_next_url_redirect_mixin import (
    ModelAdminNextUrlRedirectError,
    ModelAdminNextUrlRedirectMixin,
)
from .model_admin_redirect_on_delete_mixin import ModelAdminRedirectOnDeleteMixin
from .model_admin_replace_label_text_mixin import ModelAdminReplaceLabelTextMixin
from .templates_model_admin_mixin import TemplatesModelAdminMixin
