from .autocomplete_admin import (
    LabelSpecificationProxyAdmin,
    RegisteredSubjectProxyAdmin,
    SiteProxyAdmin,
    VisitScheduleAdmin,
)
from .dispensing_history_admin import DispensingHistoryAdmin
from .medication import (
    AssignmentAdmin,
    DosageGuidelineAdmin,
    FormulationAdmin,
    FormulationTypeAdmin,
    FrequencyUnitsAdmin,
    MedicationAdmin,
    RouteAdmin,
    UnitsAdmin,
)
from .prescription import RxAdmin, RxRefillAdmin
from .return_history_admin import ReturnHistoryAdmin
from .stock import (
    AllocationAdmin,
    ContainerAdmin,
    ContainerTypeAdmin,
    LocationAdmin,
    LotAdmin,
    OrderAdmin,
    OrderItemAdmin,
    ProductAdmin,
    ReceiveAdmin,
    ReceiveItemAdmin,
    RequestRepackAdmin,
    StockAdmin,
    StockRequestAdmin,
    StockRequestItemAdmin,
    SupplierAdmin,
)
