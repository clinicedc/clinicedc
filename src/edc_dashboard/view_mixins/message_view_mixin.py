from django.contrib import messages
from django.utils.safestring import mark_safe
# from django.contrib.messages.constants import DEFAULT_TAGS, ERROR


class MessageViewMixin:

    #     def message_user(self, message=None, level=None):
    #         tag = tag or DEFAULT_TAGS.get(ERROR)
    #         m = getattr(messages, tag)
    #         m(self.request, message=mark_safe(message))

    def message_user(self, message, level=messages.INFO, extra_tags='',
                     fail_silently=False):
        """
        Send a message to the user. The default implementation
        posts a message using the django.contrib.messages backend.

        Exposes almost the same API as messages.add_message(), but accepts the
        positional arguments in a different order to maintain backwards
        compatibility. For convenience, it accepts the `level` argument as
        a string rather than the usual level number.
        """
        if not isinstance(level, int):
            # attempt to get the level if passed a string
            try:
                level = getattr(messages.constants, level.upper())
            except AttributeError:
                levels = messages.constants.DEFAULT_TAGS.values()
                levels_repr = ', '.join('`%s`' % l for l in levels)
                raise ValueError(
                    'Bad message level string: `%s`. Possible values are: %s'
                    % (level, levels_repr)
                )

        messages.add_message(self.request, level, mark_safe(message),
                             extra_tags=extra_tags, fail_silently=fail_silently)
