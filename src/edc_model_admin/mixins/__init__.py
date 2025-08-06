from .address_model_admin_mixin import AddressModelAdminMixin
from .inlines import (
    InlineHideOriginalObjectNameMixin,
    LimitedAdminInlineMixin,
    StackedInlineModelAdminMixin,
    TabularInlineMixin,
)
from .model_admin_bypass_default_form_cls_mixin import (
    ModelAdminBypassDefaultFormClsMixin,
)
from .model_admin_form_auto_number_mixin import ModelAdminFormAutoNumberMixin
from .model_admin_form_instructions_mixin import ModelAdminFormInstructionsMixin
from .model_admin_hide_delete_button_on_condition import (
    ModelAdminHideDeleteButtonOnCondition,
)
from .model_admin_institution_mixin import ModelAdminInstitutionMixin
from .model_admin_limit_to_selected_foreignkey import (
    ModelAdminLimitToSelectedForeignkey,
)
from .model_admin_model_redirect_mixin import ModelAdminModelRedirectMixin
from .model_admin_next_url_redirect_mixin import (
    ModelAdminNextUrlRedirectError,
    ModelAdminNextUrlRedirectMixin,
)
from .model_admin_protect_pii_mixin import ModelAdminProtectPiiMixin
from .model_admin_redirect_all_to_changelist_mixin import (
    ModelAdminRedirectAllToChangelistMixin,
)
from .model_admin_redirect_on_delete_mixin import ModelAdminRedirectOnDeleteMixin
from .model_admin_replace_label_text_mixin import ModelAdminReplaceLabelTextMixin
from .templates_model_admin_mixin import TemplatesModelAdminMixin
