from .drawing_callable_example import draw_callable_example
from .site_label_configs import site_label_configs


class Container:
    qty = 128


class StockRequest:
    container = Container()


class Site:
    id = 10
    name = "Amana"


class RequestItem:
    subject_identifier = "999-99-99999-9"
    gender = "FEMALE"
    site = Site
    stock_request = StockRequest()
    code = "A9B8C7"
    sid = 99999


site_label_configs.register("test_label_config", draw_callable_example, RequestItem)
