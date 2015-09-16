import six
from django import get_version

if get_version().startswith('1.6') and six.PY2:
    try:
        from edc.base.model.validators import (
            MinConsentAge as MinConsentAgeValidator,
            MaxConsentAge as MinConsentAgeValidator,
            datetime_not_future, datetime_not_before_study_start, eligible_if_no)
        from edc.core.bhp_common.utils import formatted_age, age
    except ImportError:
        from edc_base.utils import formatted_age, age
        from edc_base.model.validators import (
            MinConsentAgeValidator, MaxConsentAgeValidator, eligible_if_no,
            datetime_not_future, datetime_not_before_study_start)
else:
        from edc_base.utils import formatted_age, age
        from edc_base.model.validators import (
            MinConsentAgeValidator, MaxConsentAgeValidator, eligible_if_no,
            datetime_not_future, datetime_not_before_study_start)
