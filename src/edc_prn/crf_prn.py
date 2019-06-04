from .prn import Prn


class CrfPrn(Prn):
    def show_on_subject_dashboard(self, subject_identifier=None, **kwargs):
        count = 0
        if self.show_on_dashboard:
            if subject_identifier:
                visit_model_attr = self.model_cls.visit_model_attr()
                opts = {f"{visit_model_attr}__subject_identifier": subject_identifier}
                count = self.model_cls.objects.filter(**opts).count()
        return True if count and self.show_on_dashboard else False
