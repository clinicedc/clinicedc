
class ConsentMeta(object):
    unique_together = (('subject_identifier', 'identity', 'version'), )
