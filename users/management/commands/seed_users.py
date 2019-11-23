from faker import Faker
from django.core.management.base import BaseCommand
from django_seed import Seed
from users.models import User

fake = Faker("ko_KR")


class Command(BaseCommand):

    help = "사용자 생성"

    def add_arguments(self, parser):
        parser.add_argument("--number", default=2, type=int, help="몇 명의 사용자를 만들까요?")

    def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        seeder.add_entity(
            User,
            number,
            {
                "username": lambda x: fake.email(),
                "password": "password",
                "name": lambda x: fake.name(),
                "email": lambda x: fake.email(),
                "is_staff": False,
                "is_superuser": False,
            },
        )
        seeder.execute()

        self.stdout.write(self.style.SUCCESS(f"{number}명의 사용자가 생성되었습니다!"))
