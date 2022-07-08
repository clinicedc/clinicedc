from uuid import uuid4

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from edc_label import Label
from edc_protocol import Protocol


@admin.action(permissions=["view"], description="Print medication stock labels")
def print_stock_labels(modeladmin, request, queryset):
    zpl_data = []
    label = Label(
        label_template_name="stock_label.lbl",
        static_files_path="edc_pharmacy/label_templates",
    )
    for obj in queryset:
        for i in range(1, obj.qty):
            stock_identifier = uuid4().hex
            context = dict(
                protocol=Protocol().protocol,
                protocol_title=Protocol().protocol_title,
                stock_identifier=stock_identifier,
                barcode_value=stock_identifier,
                medication_name=obj.product.formulation.medication.display_name,
                medication_strength=obj.product.formulation.strength,
                medication_units=obj.product.formulation.units,
            )
            # keys = [k for k in context]
            # for fld in obj._meta.get_fields():
            #     if fld.name not in keys and fld.name != "assignment":
            #         context.update({fld.name: getattr(obj, fld.name)})
            zpl_data.append(
                str(label.render_as_zpl_data(copies=1, context=context, encoding=False))
                .strip("\n")
                .replace("\n", "")
            )
    request.session["zpl_data"] = "|".join(zpl_data)
    url = reverse("edc_label:browser_print_labels_url")
    return HttpResponseRedirect(url)
