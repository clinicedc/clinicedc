
class MailingList:

    def __init__(self, notification):
        self.list_email = notification.email_to
        self.display_name = notification.display_name

    def subscribe(self, email):
        print(
            f'{email} added to mailing list {self.list_email} for {self.display_name}.')

    def unsubscribe(self, email):
        print(
            f'{email} removed from mailing list {self.list_email} for {self.display_name}.')
