from .autocomplete_admin import (
    LabelSpecificationProxyAdmin,
    SiteProxyAdmin,
    SubjectAdmin,
    VisitScheduleAdmin,
)
from .dispensing_history_admin import DispensingHistoryAdmin
from .medication import (
    AssignmentAdmin,
    DosageGuidelineAdmin,
    FormulationAdmin,
    FormulationTypeAdmin,
    FrequencyUnitsAdmin,
    LotAdmin,
    MedicationAdmin,
    RouteAdmin,
    UnitsAdmin,
)
from .prescription import RxAdmin, RxRefillAdmin
from .return_history_admin import ReturnHistoryAdmin
from .stock import (
    ContainerAdmin,
    ContainerTypeAdmin,
    OrderAdmin,
    OrderItemAdmin,
    ProductAdmin,
    ReceiveAdmin,
    ReceiveItemAdmin,
    RequestRepackAdmin,
    StockAdmin,
    StockRequestAdmin,
    StockRequestItemAdmin,
    StockUpdateAdmin,
)
