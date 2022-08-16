def get_reference_range_collection_name(obj) -> str:
    """Returns the reference range name.

    Expects either a model with requisition attr or a requisition.

    See edc_reference.
    """
    try:
        return obj.requisition.panel_object.reference_range_collection_name
    except AttributeError:
        return obj.panel_object.reference_range_collection_name
