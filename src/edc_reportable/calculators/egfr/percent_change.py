def egfr_percent_change(egfr_value: float, baseline_egfr_value: float) -> float:
    """Returns the percent change from baseline"""
    if egfr_value and baseline_egfr_value:
        return 100 * (
            (float(baseline_egfr_value) - float(egfr_value)) / float(baseline_egfr_value)
        )
    return 0.0
