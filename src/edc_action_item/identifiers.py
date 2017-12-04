from edc_identifier.simple_identifier import SimpleUniqueIdentifier, SimpleTimestampIdentifier


class ActionIdentifier(SimpleUniqueIdentifier):
    random_string_length = 2
    identifier_type = 'action_identifier'
    identifier_prefix = 'AC'
    template = '{device_id}{timestamp}{random_string}'
    identifier_cls = SimpleTimestampIdentifier
    make_human_readable = True
