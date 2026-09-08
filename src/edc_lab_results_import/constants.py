ERROR = "error"
IMPORTED = "imported"
RESOLVED = "resolved"
PENDING = "pending"

# result comparison, see `ResultComparison`
MATCH = "match"
DIFFERS = "differs"
NOT_COMPARED = "not_compared"

# a `Result.flag` in this set means the lab called the value abnormal,
# so the CRF is expected to say abnormal=YES. A blank flag means NO.
# Anything else is not interpreted.
ABNORMAL_FLAGS = ("h", "hh", "l", "ll")

# orphan result buckets, see `get_df_orphan_results`
VISIT_NOT_FOUND = "visit_not_found"
RESOLVER_MISS = "resolver_miss"
REQUISITION_NOT_KEYED = "requisition_not_keyed"
PANEL_NOT_EXPECTED = "panel_not_expected"
