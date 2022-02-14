from django.db import models


# Create your models here.
class AbstractSubscriber(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    gdpr_consent = models.BooleanField()

    class Meta:
        abstract = True


class Subscriber(AbstractSubscriber):
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"u {self.id} {self.email}"


class SubscriberSMS(AbstractSubscriber):
    phone = models.TextField(unique=True)

    def __str__(self):
        return f"u {self.id} {self.phone}"


class Client(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    phone = models.TextField()

    def __str__(self):
        return f"c {self.id} {self.email} {self.phone}"

class User(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(null=True)
    phone = models.TextField(null=True)
    gdpr_consent = models.BooleanField()

    def __str__(self):
        return f"u {self.id} {self.email} {self.phone}"




