from django.core.management.base import BaseCommand
from django.utils import timezone

from a1.models import Subscriber, SubscriberSMS, User, Client


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        self._create_subscribers()
        self._create_subscribersSMS()
        self._create_user()
        self._create_client()
        self._create_conflicted_client_vs_users()

    def _create_subscribers(self):
        subscribers = (Subscriber(gdpr_consent=True, email=f"{x}@wp.pl") for x in range(1, 21))
        Subscriber.objects.bulk_create(subscribers)

    def _create_subscribersSMS(self):
        subscribers = (SubscriberSMS(gdpr_consent=True, phone=x) for x in range(21, 41))
        SubscriberSMS.objects.bulk_create(subscribers)

    def _create_user(self):
        user = (User(gdpr_consent=True, email=f"{x}@wp.pl", phone=x + 5) for x in range(1, 11))
        User.objects.bulk_create(user)

    def _create_client(self):
        client = (Client(email=f"{x}@wp.pl", phone=22 + x) for x in range(5, 16))
        Client.objects.bulk_create(client)
        client = (Client(email=f"{x}@wp.pl", phone=22 + x) for x in range(14, 16))
        Client.objects.bulk_create(client)

    def _create_conflicted_client_vs_users(self):
        subscribers = (Subscriber(gdpr_consent=True, email=f"{x}conflict@wp.pl") for x in range(3, 7))
        Subscriber.objects.bulk_create(subscribers)
        client = (Client(email=f"{x}conflict@wp.pl", phone=100 + x) for x in range(3, 7))
        Client.objects.bulk_create(client)
        user = (User(gdpr_consent=True, email=f"{x}conflict2@wp.pl", phone=100 + x) for x in range(3, 7))
        User.objects.bulk_create(user)
