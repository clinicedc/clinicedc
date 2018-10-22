import requests

from django.conf import settings
import sys


class EmailNotEnabledError(Exception):
    pass


class MailingListManager:

    url = 'https://api.mailgun.net/v3/lists'

    def __init__(self, email_to=None, name=None, display_name=None, description=None):
        self.description = description
        self.display_name = display_name
        try:
            self.email_to = email_to[0]
        except IndexError:
            self.email_to = email_to
        self.name = name

    def subscribe(self, user, verbose=None):
        """Returns a response after attempting to subscribe
        a member to the list.
        """
        if not settings.EMAIL_ENABLED:
            raise EmailNotEnabledError('See settings.EMAIL_ENABLED')
        response = requests.post(
            f"{self.url}/{self.email_to}/members",
            auth=('api', settings.MAILGUN_API_KEY),
            data={'subscribed': True,
                  'address': user.email,
                  'name': f'{user.first_name} {user.last_name}',
                  'description': f'{user.userprofile.job_title or ""}'})
        if verbose:
            sys.stdout.write(
                f'Subscribing user {user.username}. '
                f'Got {response.status_code}: \"{response.json().get("message")}\"\n')
        return response

    def unsubscribe(self, user, verbose=None):
        """Returns a response after attempting to unsubscribe
        a member from the list.
        """
        if not settings.EMAIL_ENABLED:
            raise EmailNotEnabledError('See settings.EMAIL_ENABLED')
        response = requests.put(
            f"{self.url}/{self.email_to}/members/{user.email}",
            auth=('api', settings.MAILGUN_API_KEY),
            data={'subscribed': False})
        if verbose:
            sys.stdout.write(
                f'Unsubscribing user {user.username}. '
                f'Got {response.status_code}: \"{response.json().get("message")}\"\n')
        return response

    def create(self):
        """Returns a response after attempting to create the list.
        """
        if not settings.EMAIL_ENABLED:
            raise EmailNotEnabledError('See settings.EMAIL_ENABLED')
        return requests.post(
            self.url,
            auth=('api', settings.MAILGUN_API_KEY),
            data={'address': self.email_to,
                  'name': self.name,
                  'description': self.description or self.display_name})

    def delete(self):
        """Returns a response after attempting to delete the list.
        """
        if not settings.EMAIL_ENABLED:
            raise EmailNotEnabledError('See settings.EMAIL_ENABLED')
        return requests.delete(
            f'{self.url}/{self.email_to}',
            auth=('api', settings.MAILGUN_API_KEY))

    def delete_member(self, user):
        """Returns a response after attempting to remove
        a member from the list.
        """
        if not settings.EMAIL_ENABLED:
            raise EmailNotEnabledError('See settings.EMAIL_ENABLED')
        return requests.delete(
            f"{self.url}/{self.email_to}/members/{user.email}",
            auth=('api', settings.MAILGUN_API_KEY))
