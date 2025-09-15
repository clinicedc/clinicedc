import usb
import usb.core
import usb.util
from django.http import JsonResponse


class FindDevices:
    def __init__(self, class_):
        self._class = class_

    def __call__(self, device):
        if device.bDeviceClass == self._class:
            return True
        for cfg in device:
            intf = usb.util.find_descriptor(cfg, bInterfaceClass=self._class)
            if intf is not None:
                return True
        return False


def list_usb_printers():
    printers = usb.core.find(find_all=1, custom_match=FindDevices(7))
    return [f"{dev.manufacturer} {dev.product}" for dev in printers]


def print_label_usb(request):
    """
    see pyusb
    https://github.com/pyusb/pyusb/blob/master/docs/tutorial.rst

    usb module requires ...
        linux: sudo apt-get install libusb-1.0-0-dev
        mac: brew install libusb
        windows: download the libusb DLL from the libusb
            website and place it in your system directory
    """
    if request.method == "POST":
        zpl_code = request.body.decode("utf-8")
        dev = usb.core.find(idVendor=0x0A5F)  # Replace with your printer's vendor ID
        if dev is None:
            return JsonResponse({"error": "Printer not found"}, status=404)

        dev.set_configuration()
        cfg = dev.get_active_configuration()
        intf = cfg[(0, 0)]
        ep = usb.util.find_descriptor(
            intf,
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress)
            == usb.util.ENDPOINT_OUT,
        )

        if ep is None:
            return JsonResponse({"error": "Endpoint not found"}, status=404)

        ep.write(zpl_code)
        return JsonResponse({"message": "Label sent to printer"}, status=200)
    return JsonResponse({"error": "Invalid request method"}, status=400)
