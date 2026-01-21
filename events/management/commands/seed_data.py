from django.core.management.base import BaseCommand
from faker import Faker
import random
from django.contrib.auth.models import User, Group

from events.models import Category, Event

class Command(BaseCommand):
    help = 'Seed database with fake events, categories and users'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Ensure groups exist
        participant_group, _ = Group.objects.get_or_create(name="Participant")
        organizer_group, _ = Group.objects.get_or_create(name="Organizer")
        admin_group, _ = Group.objects.get_or_create(name="Admin")

        # Create Categories
        categories = []
        for _ in range(5):
            cat = Category.objects.create(
                name=fake.word().title(),
                description=fake.sentence()
            )
            categories.append(cat)

        # Create Users
        users = []
        for _ in range(20):
            user = User.objects.create_user(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password='password123'  # For testing purposes
            )
            # Assign random roles
            if random.random() < 0.1:  # 10% admins
                user.groups.add(admin_group)
            elif random.random() < 0.3:  # 30% organizers (of remaining)
                user.groups.add(organizer_group)
            else:  # 60% participants
                user.groups.add(participant_group)
            users.append(user)

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
                random.sample(users, random.randint(3, 8))
            )

        self.stdout.write(
            self.style.SUCCESS('Successfully seeded database with fake data')
        )
