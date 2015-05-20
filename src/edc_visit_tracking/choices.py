# you'll probably use a local tuple for the VISIT_REASON. See visit model method get_visit_reason_choices()
VISIT_REASON = (
    ('scheduled', 'Scheduled visit/contact'),
    ('unscheduled', 'Unscheduled visit/contact'),
    ('missed', 'Missed visit'),
    ('lost', 'Lost to follow-up (use only when taking subject off study)'),
    ('deferred', 'Deferred'),
    ('death', 'Death'),
    ('off study', 'Off Study')
)
