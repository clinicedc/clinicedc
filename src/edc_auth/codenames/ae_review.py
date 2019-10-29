from .ae import ae


ae_review = [c for c in ae if ("view_" in c or "edc_nav" in c or "edc_dashboard" in c)]
