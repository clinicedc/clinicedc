from django.apps import apps as django_apps
from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import color_style

style = color_style()


class Command(BaseCommand):
    help = "Update search slugs if 'get_slugs' " "method definitions have changed."

    def add_arguments(self, parser):
        parser.add_argument(
            "model",
            nargs="+",
            type=str,
            help=(
                "a model name or list of model names in label_lower format. "
                "If no model names are specified then all models configured "
                "to use a search slug will be updated."
            ),
        )

    def handle(self, *args, **options):
        if options.get("model"):
            models = []
            for model_name in options.get("model"):
                models.append(django_apps.get_model(*model_name.split(".")))
        else:
            models = args or django_apps.get_models()
        for model in models:
            if "historical" not in model._meta.label_lower:
                if hasattr(model, "update_search_slugs"):
                    self.stdout.write(
                        self.style.WARNING(
                            "Updating '{}' ...".format(model._meta.label_lower)
                        ),
                        ending="\r",
                    )
                    try:
                        model.objects.update_search_slugs()
                    except AttributeError as e:
                        if "update_search_slugs" in str(e):
                            raise CommandError(
                                "Missing manager method 'update_search_slugs'. "
                                "See model {}. Got {}".format(model._meta.label_lower, str(e))
                            )
                        else:
                            raise CommandError(e)
                    except Exception as e:
                        raise CommandError(
                            "An exception occurred when updating model {}. "
                            "Got {}".format(model._meta.label_lower, e)
                        )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(
                                "Updating '{}' ... Done".format(model._meta.label_lower)
                            )
                        )
                else:
                    self.stdout.write("------- {}".format(model._meta.label_lower))
