from .base_requisition_factory import BaseRequisitionFactory


class BaseClinicRequisitionFactory(BaseRequisitionFactory):
    class Meta:
        abstract = True
