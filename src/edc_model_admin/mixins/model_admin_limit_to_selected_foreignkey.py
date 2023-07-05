from typing import Any, Tuple

from django.core.handlers.wsgi import WSGIRequest

NAME = 0
MODEL_CLS = 1


class ModelAdminLimitToSelectedForeignkeyError(Exception):
    pass


class ModelAdminLimitToSelectedForeignkey:
    limit_fk_field_to_selected: list[Tuple[str, Any]] = None

    def formfield_for_foreignkey(self, db_field, request: WSGIRequest, **kwargs):
        db = kwargs.get("using")
        if db_field.name in [item[NAME] for item in self.limit_fk_field_to_selected]:
            model_cls = None
            for item in self.limit_fk_field_to_selected:
                if item[NAME] == db_field.name:
                    model_cls = item[MODEL_CLS]
                    break
            if not model_cls:
                raise ModelAdminLimitToSelectedForeignkeyError(
                    f"Invalid model or model not found. Got {(db_field.name, model_cls)}"
                )
            if request.GET.get(db_field.name):
                kwargs["queryset"] = model_cls.on_site.using(db).filter(
                    id__exact=request.GET.get(db_field.name, 0)
                )
            else:
                kwargs["queryset"] = model_cls.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
