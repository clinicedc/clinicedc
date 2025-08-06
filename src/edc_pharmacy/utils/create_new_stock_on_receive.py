from uuid import UUID

from django.apps import apps as django_apps


def create_new_stock_on_receive(receive_item_pk: UUID = None):
    receive_item_model_cls = django_apps.get_model("edc_pharmacy.receiveitem")
    stock_model_cls = django_apps.get_model("edc_pharmacy.stock")
    receive_item = receive_item_model_cls.objects.get(pk=receive_item_pk)
    for i in range(0, int(receive_item.qty)):
        stock_model_cls.objects.create(
            receive_item_id=receive_item.id,
            qty_in=1,
            qty_out=0,
            qty=1,
            product_id=receive_item.order_item.product.id,
            container_id=receive_item.container.id,
            location_id=receive_item.receive.location.id,
            lot_id=receive_item.lot.id,
        )
