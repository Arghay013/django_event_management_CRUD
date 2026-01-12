from django.core.management.base import BaseCommand
from faker import Faker
import random

from events.models import Category, Event, Participant

class Command(BaseCommand):
    help = 'Seed database with fake events, categories and participants'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create Categories
        categories = []
        for _ in range(5):
            cat = Category.objects.create(
                name=fake.word().title(),
                description=fake.sentence()
            )
            categories.append(cat)

        # Create Participants
        participants = []
        for _ in range(20):
            p = Participant.objects.create(
                name=fake.name(),
                email=fake.unique.email()
            )
            participants.append(p)

        # Create Events
        for _ in range(10):
            event = Event.objects.create(
                name=fake.catch_phrase(),
                description=fake.text(),
                date=fake.date_between(start_date='-5d', end_date='+10d'),
                time=fake.time(),
                location=fake.city(),
                category=random.choice(categories)
            )
            event.participants.set(
                random.sample(participants, random.randint(3, 8))
            )
