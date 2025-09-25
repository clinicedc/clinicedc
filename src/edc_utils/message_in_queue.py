from django.contrib.messages import get_messages


def message_in_queue(request, message_text):
    storage = get_messages(request)
    return any(message.message == message_text for message in storage)
