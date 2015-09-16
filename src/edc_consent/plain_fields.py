from django import get_version

if get_version().startswith('1.6'):
    try:
        from edc.base.model.fields import IdentityTypeField
        from edc.base.model.fields import IsDateEstimatedField
    except ImportError:
        from edc_base.model.fields import IdentityTypeField
        from edc_base.model.fields import IsDateEstimatedField
else:
    from edc_base.model.fields import IdentityTypeField
    from edc_base.model.fields import IsDateEstimatedField
