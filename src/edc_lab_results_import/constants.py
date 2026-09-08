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
