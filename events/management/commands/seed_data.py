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

        # ----- FIXED USERS -----
        organizer_user, created = User.objects.get_or_create(
            username="arghay_deb",
            defaults={
                "email": "organizer@test.com",
                "first_name": "Arghay",
                "last_name": "Deb",
                "is_active": True
            }
        )
        organizer_user.set_password("1234")
        organizer_user.save()
        organizer_user.groups.add(organizer_group)

        participant_user, created = User.objects.get_or_create(
            username="arghay013",
            defaults={
                "email": "participant@test.com",
                "first_name": "Arghay",
                "last_name": "Paul",
                "is_active": True
            }
        )
        participant_user.set_password("1234")
        participant_user.save()
        participant_user.groups.add(participant_group)

        # ----- Categories -----
        categories = []
        for _ in range(5):
            name = fake.word().title()
            cat, _ = Category.objects.get_or_create(
                name=name,
                defaults={"description": fake.sentence()}
            )
            categories.append(cat)

        # ----- Random Users -----
        users = [organizer_user, participant_user]  # Always include fixed users
        for _ in range(20):
            username = fake.unique.user_name()
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": fake.unique.email(),
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                }
            )
            if created:
                user.set_password("password123")
                user.save()
                # Assign random roles
                if random.random() < 0.1:
                    user.groups.add(admin_group)
                elif random.random() < 0.3:
                    user.groups.add(organizer_group)
                else:
                    user.groups.add(participant_group)
            users.append(user)

        # ----- Events -----
        for _ in range(10):
            event_name = fake.catch_phrase()
            event, created = Event.objects.get_or_create(
                name=event_name,
                defaults={
                    "description": fake.text(),
                    "date": fake.date_between(start_date='-5d', end_date='+10d'),
                    "time": fake.time(),
                    "location": fake.city(),
                    "category": random.choice(categories)
                }
            )
            # Assign participants if newly created
            if created:
                event.participants.set(random.sample(users, random.randint(3, 8)))

        self.stdout.write(
            self.style.SUCCESS('Successfully seeded database with fake data (no duplicates, fixed users present)')
        )