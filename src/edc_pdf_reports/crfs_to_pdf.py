import os

import pdfkit
import requests
from edc_visit_schedule import site_visit_schedules


class CrfToPdf:

    """Experimental"""

    login_url = "http://localhost:8000/accounts/login/"

    pdf_options = {
        "page-size": "A4",
        "margin-top": "2cm",
        "margin-right": "2cm",
        "margin-bottom": "2cm",
        "margin-left": "2cm",
        "encoding": "UTF-8",
        "custom-header": [("Accept-Encoding", "gzip")],
        "no-outline": None,
    }

    def __init__(self, path, visit_schedule=None, username=None, password=None):
        self.forms = {}
        self.visit_schedule = visit_schedule
        self.payload = dict(
            username=username,
            password=password,
            csrfmiddlewaretoken=None,
            next=None,
        )
        self.path = os.path.expanduser(path)
        self.update()

    @staticmethod
    def crf_name_to_url(label_lower):
        app_label, model_name = label_lower.split(".")
        return f"/admin/{app_label}/{model_name}/add/"

    def request_add_form_text(self, next_url):
        with requests.Session() as session:
            session.get(self.login_url)
            csrf_token = session.cookies["csrftoken"]
            self.payload.update(csrfmiddlewaretoken=csrf_token, next=next_url)
            post = session.post(self.login_url, data=self.payload)
            return post.text

    def update(self):
        for visit_schedule in site_visit_schedules.visit_schedules.values():
            for schedule in visit_schedule.schedules.values():
                for visit in schedule.visits.values():
                    for crf in visit.crfs:
                        if crf.model not in self.forms:
                            next_url = self.crf_name_to_url(crf.model)
                            print(next_url)
                            self.forms.update(
                                {crf.model: self.request_add_form_text(next_url)}
                            )

    def to_pdf(self, key=None):
        if key:
            return self._to_pdf(key)
        else:
            for k in self.forms:
                self._to_pdf(k)

    def _to_pdf(self, key=None):
        filename = os.path.join(self.path, f"{key}.pdf")
        print(f"writing {filename}")
        pdfkit.from_string(
            self.forms.get(key),
            filename,
            options=self.pdf_options,
        )
        return filename
