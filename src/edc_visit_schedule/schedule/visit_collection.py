from ..ordered_collection import OrderedCollection


class VisitCollection(OrderedCollection):

    key = 'code'
    ordering_attr = 'timepoint'
