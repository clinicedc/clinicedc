from .lab import lab

lab_view = [c for c in lab if ("view_" in c or "edc_nav" in c or "edc_dashboard" in c)]
