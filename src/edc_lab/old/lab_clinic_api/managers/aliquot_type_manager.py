from django.db import models


class AliquotTypeManager(models.Manager):

    def get_by_natural_key(self, alpha_code, numeric_code):
        return self.get(alpha_code=alpha_code, numeric_code=numeric_code)
