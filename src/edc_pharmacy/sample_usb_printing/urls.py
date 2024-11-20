from django.urls import path

from .usb_printing import print_label_usb

path("print_label_usb/", print_label_usb, name="print_label_usb"),
