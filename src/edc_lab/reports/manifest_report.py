import os

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer)
from reportlab.graphics.barcode import code39
from reportlab.lib.units import mm, cm

from django.apps import apps as django_apps
from django.conf import settings
from django.http import HttpResponse


from .numbered_canvas import NumberedCanvas
from .report import Report


class ManifestReport(Report):

    def __init__(self, manifest=None, **kwargs):
        super().__init__(**kwargs)
        app_config = django_apps.get_app_config('edc_lab')
        self.manifest = manifest
        self.box_model = django_apps.get_model(
            *app_config.box_model.split('.'))
        self.aliquot_model = django_apps.get_model(
            *app_config.aliquot_model.split('.'))
        self.requisition_model = django_apps.get_model(
            *app_config.requisition_model.split('.'))
        self.image_folder = os.path.join(
            settings.STATIC_ROOT, 'bcpp', 'images')

    @property
    def export_data(self):
        return {
            'company': 'company',
            'address': 'address',
            'city': 'city',
            'state_code': 'state_code',
            'postal_code': 'postal_code',
            'country_code': 'country_code',
            'export_country': 'export_country',
            'destination_country': 'destination_country',
            'manifest_identifier': self.manifest.human_readable_identifier,
            'manifest_date': self.manifest.manifest_datetime.strftime('%Y-%m-%d %H:%M'),
            'export_date': self.manifest.manifest_datetime.strftime('%Y-%m-%d %H:%M'),
            'export_refs': 'export_refs',
            'country_of_origin': 'country_of_origin',
        }

    @property
    def exporter_data(self):
        return {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'address': 'address',
            'city': 'city',
            'state_code': 'state_code',
            'postal_code': 'postal_code',
            'country_code': 'country_code',
        }

    @property
    def consignee_data(self):
        return {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'address': 'address',
            'city': 'city',
            'state_code': 'state_code',
            'postal_code': 'postal_code',
            'country_code': 'country_code',
        }

    @property
    def company_address(self, **kwargs):
        company_address = {
            'address': 'address',
            'city': 'city',
            'state_code': 'state_code',
            'postal_code': 'postal_code',
            'country_code': 'country_code',
        }
        company_address.update(**kwargs)
        return ('{address}<br />{city}, '
                '{state_code}<br />'
                '{postal_code} {country_code}'.format(**company_address))

    @property
    def address_paragraph(self, **kwargs):
        address_paragraph = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'address': 'address',
            'city': 'city',
            'state_code': 'state_code',
            'postal_code': 'postal_code',
            'country_code': 'country_code',
        }
        address_paragraph.update(**kwargs)
        return ('{first_name}, {last_name}<br />'
                '{address}<br />'
                '{city}, {state_code} <br />'
                '{postal_code}, <br />'
                '{country_code}'.format(**address_paragraph))

    def render(self, export_data=None, consignee_data=None, exporter_data=None,
               company_address=None, **kwargs):
        if export_data:
            self.export_data = export_data
        if consignee_data:
            self.consignee_data = consignee_data
        if exporter_data:
            self.exporter_data = exporter_data
        if company_address:
            self.company_address = company_address

        response = HttpResponse(content_type='application/pdf')
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer, rightMargin=.5 * cm, leftMargin=.5 * cm,
            topMargin=1.5 * cm, bottomMargin=1.5 * cm,
            pagesize=A4)

        story = []

        data = [
            [Paragraph(
                self.export_data['company'], self.styles["line_data_large"])],
            [Paragraph('SITE NAME', self.styles["line_label"])],
            [Paragraph(self.company_address, self.styles["line_data_large"])],
            [Paragraph('SITE DETAILS', self.styles["line_label"])]]

        t = Table(data, colWidths=(9 * cm))
        t.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (0, 1), 0.25, colors.black),
            ('INNERGRID', (0, 2), (0, 3), 0.25, colors.black)]))
        t.hAlign = 'RIGHT'

        story.append(t)

        story.append(Spacer(0.1 * cm, .5 * cm))

        story.append(
            Paragraph("SPECIMEN MANIFEST", self.styles["line_label_center"]))

        data = [
            [Paragraph('MANIFEST NO.', self.styles["line_label"]),
             Paragraph(
                 self.export_data['manifest_identifier'], self.styles["line_data_largest"]),
             Paragraph('<b>NOTE: All specimens must be <br /> '
                       'verfied on the EDC before release <br /> '
                       'from the site.</b>', self.styles["line_data_small"]),
             ]]
        t = Table(data, colWidths=(3 * cm, None, 4.5 * cm,))
        t.setStyle(TableStyle([
            ('INNERGRID', (1, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        story.append(t)

        data = [[Paragraph('MANIFEST DATE', self.styles["line_label"]),
                 Paragraph('EXPORT REFERENCES (i.e. order no., invoice no.)', self.styles["line_label"])],
                [Paragraph(self.export_data['manifest_date'], self.styles["line_data_largest"]),
                 Paragraph(
                    self.export_data['export_refs'], self.styles["line_data_largest"]),
                 ]]
        t = Table(data)
        t.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (1, 0), 0.25, colors.black),
            ('INNERGRID', (0, 1), (1, 1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t)

        cosignee_paragraph = self.address_paragraph.format(
            **self.consignee_data)
        exporter_paragraph = self.address_paragraph.format(
            **self.exporter_data)

        data = [[Paragraph('SHIPPER/EXPORTER (complete name and address)', self.styles["line_label"]),
                 Paragraph('CONSIGNEE (complete name and address)', self.styles["line_label"])],

                [Paragraph(cosignee_paragraph, self.styles["line_data_large"]),
                 Paragraph(exporter_paragraph, self.styles["line_data_large"])]
                ]

        t = Table(data)
        t.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (1, 0), 0.25, colors.black),
            ('INNERGRID', (0, 1), (1, 1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t)

        importer_data = {}
        if not importer_data:
            importer_data = {'first_name': '', 'last_name': '',
                             'postal_code': '', 'country_code': '', 'state_code': '',
                             'city': '', 'address': ''}
            importer_paragraph = 'importer_paragraph'
        else:
            importer_paragraph = self.address_paragraph.format(**importer_data)

        data1 = [[Paragraph('COUNTRY OF EXPORT', self.styles["line_label"]),
                  Paragraph('DESCRIPTION OF CONTENTS <br />', self.styles["line_label"])],
                 [Paragraph(self.export_data['export_country'], self.styles["line_data_largest"]),
                  Paragraph(importer_paragraph, self.styles["line_data_large"])],
                 [Paragraph(
                     'COUNTRY OF ORIGIN', self.styles["line_label"]), ''],
                 [Paragraph(
                     self.export_data['country_of_origin'], self.styles["line_data_largest"]), ''],
                 [Paragraph(
                     'COUNTRY OF ULTIMATE DESTINATION', self.styles["line_label"]), ''],
                 [Paragraph(
                     self.export_data['destination_country'], self.styles["line_data_largest"]), ''],
                 ]
        t1 = Table(data1)
        t1.setStyle(TableStyle([
            ('INNERGRID', (0, 1), (0, 2), 0.25, colors.black),
            ('INNERGRID', (0, 3), (0, 4), 0.25, colors.black),
            ('INNERGRID', (0, 0), (1, 0), 0.25, colors.black),
            ('INNERGRID', (0, 1), (1, 1), 0.25, colors.black),
            ('INNERGRID', (0, 2), (1, 2), 0.25, colors.black),
            ('INNERGRID', (0, 3), (1, 3), 0.25, colors.black),
            ('INNERGRID', (0, 4), (1, 4), 0.25, colors.black),
            ('INNERGRID', (0, 5), (1, 5), 0.25, colors.black),
            ('SPAN', (1, 1), (1, 5)),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t1)

#         checked_image_path = os.path.join(
#             self.image_folder, 'checked.png')
#         unchecked_image_path = os.path.join(
#             self.image_folder, 'unchecked.png')
#
#         flags = {
#             'fob': None,
#             'caf': True,
#             'cif': None,
#         }
#         flag_image_paths = {}
#         for key, value in flags.items():
#             flag_image_paths[
#                 key] = checked_image_path if value else unchecked_image_path
#
#         check_data = [[Paragraph('Check one', self.styles["line_label"]), ''],
#                       [Image(flag_image_paths['fob'], .25 * cm, .25 * cm),
#                        Paragraph('F.O.B.', self.styles["line_label"])],
#                       [Image(flag_image_paths['caf'], .25 * cm, .25 * cm),
#                        Paragraph('C & F', self.styles["line_label"])],
#                       [Image(flag_image_paths['cif'], .25 * cm, .25 * cm),
#                        Paragraph('C.I.F.', self.styles["line_label"])]]
#         tc = Table(check_data, colWidths=(.4 * cm, None))
#         tc.setStyle(TableStyle([
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('SPAN', (0, 0), (1, 0)),
#         ]))

        story.append(Spacer(0.1 * cm, .5 * cm))

        story.append(Table([[Paragraph('I DECLARE THE INFORMATION CONTAINED IN THIS '
                                       'MANIFEST TO BE TRUE AND CORRECT', self.styles["line_label"])]]))

        story.append(Spacer(0.1 * cm, .5 * cm))

        # TODO: signature could be image ? Date could be sign_date ?
        # TODO: signature, date
        data1 = [
            [Paragraph(self.export_data['company'], self.styles["line_data_large"]), '',
             Paragraph(
                 self.export_data['export_date'], self.styles["line_data_large"])
             ],
            [Paragraph('SIGNATURE OF SHIPPER/EXPORTER (Type name and title and sign.)', self.styles["line_label"]), '',
             Paragraph('DATE', self.styles["line_label"])]]

        t1 = Table(data1, colWidths=(None, 2 * cm, None))
        t1.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (0, 1), 0.25, colors.black),
            ('INNERGRID', (2, 0), (2, 1), 0.25, colors.black),
        ]))

        story.append(t1)
        story.append(Spacer(0.1 * cm, .5 * cm))

        # boxes
        story.append(
            Table([[Paragraph('MANIFEST CONTENTS', self.styles["line_label_center"])]]))

        box_header = [
            Paragraph('BOX:', self.styles["line_label"]),
            Paragraph(
                'CATEGORY:', self.styles["line_label"]),
            Paragraph('SPECIMEN TYPES:', self.styles["line_label"]),
            Paragraph('ITEM COUNT:', self.styles["line_label"]),
            Paragraph('BOX DATE:', self.styles["line_label"])]
        for index, manifest_item in enumerate(
                self.manifest.manifestitem_set.all().order_by('-created')):
            if index > 0:
                story.append(Spacer(0.1 * cm, .5 * cm))
            data1 = []
            data1.append(box_header)
            box = self.box_model.objects.get(
                box_identifier=manifest_item.identifier)
            barcode = code39.Standard39(
                box.box_identifier, barHeight=5 * mm, stop=1)
            data1.append([
                Paragraph(
                    box.box_identifier, self.styles["line_data_large"]),
                Paragraph(
                    box.get_category_display().upper(), self.styles["line_data_large"]),
                Paragraph(box.specimen_types, self.styles["line_data_large"]),
                Paragraph(
                    '{}/{}'.format(str(box.count), str(box.box_type.total)), self.styles["line_data_large"]),
                Paragraph(box.box_datetime.strftime('%Y-%m-%d'), self.styles["line_data_large"])])
            t1 = Table(
                data1, colWidths=(None, 3 * cm, 3 * cm, 3 * cm, 3 * cm))
            t1.setStyle(TableStyle([
                ('INNERGRID', (0, 0), (-1, 0), 0.25, colors.black),
                ('INNERGRID', (0, 1), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ]))
            story.append(t1)
            story.append(Spacer(0.1 * cm, .5 * cm))

            table_data = []
            table_data = [[
                Paragraph('BARCODE', self.styles["line_label_center"]),
                Paragraph('POS', self.styles["line_label_center"]),
                Paragraph(
                    'ALIQUOT IDENTIFIER', self.styles["line_label_center"]),
                Paragraph('SUBJECT', self.styles["line_label_center"]),
                Paragraph('TYPE', self.styles["line_label_center"]),
                Paragraph('DATE', self.styles["line_label_center"]),
            ]]
            for box_item in box.boxitem_set.all().order_by('position'):
                aliquot = self.aliquot_model.objects.get(
                    aliquot_identifier=box_item.identifier)
                requisition = self.requisition_model.objects.get(
                    requisition_identifier=aliquot.requisition_identifier)
                barcode = code39.Standard39(
                    aliquot.aliquot_identifier, barHeight=5 * mm, stop=1)
                table_data.append([
                    barcode,
                    Paragraph(str(box_item.position), self.styles['row_data']),
                    Paragraph(
                        aliquot.human_readable_identifier, self.styles['row_data']),
                    Paragraph(
                        aliquot.subject_identifier, self.styles['row_data']),
                    Paragraph('{} ({}) {}'.format(
                        aliquot.aliquot_type,
                        aliquot.numeric_code,
                        requisition.panel_object.abbreviation), self.styles['row_data']),
                    Paragraph(aliquot.aliquot_datetime.strftime(
                        '%Y-%m-%d'), self.styles['row_data']),
                ])
                t1 = Table(table_data)
                t1.setStyle(TableStyle([
                    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.black)]))
            story.append(t1)

        doc.build(story, onFirstPage=self._header_footer, onLaterPages=self._header_footer,
                  canvasmaker=NumberedCanvas)
        pdf = buffer.getvalue()
        response.write(pdf)
        return response
