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
PANEL_UNKNOWN = "panel_unknown"
PANEL_NOT_EXPECTED = "panel_not_expected"

# a specimen collected on or before a subject's first visit cannot
# belong to a later timepoint, so baseline is the only candidate. This
# bounds how far before, since "on or before" alone would also claim a
# specimen drawn a year earlier. See `add_baseline_candidate` and
# `ResultImporter.match_baseline_visits`.
MAX_DAYS_BEFORE_BASELINE = 30
ON_OR_BEFORE_BASELINE = "on_or_before_baseline"
