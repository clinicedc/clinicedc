from django.contrib.messages import get_messages


def message_in_queue(request, message_text):
    storage = get_messages(request)
    for message in storage:
        if message.message == message_text:
            return True
    return False
