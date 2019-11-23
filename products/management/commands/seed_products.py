import random
from datetime import datetime, timedelta

# from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.admin.utils import flatten
from django_seed import Seed
from products import models as product_models
from users import models as user_models


# fake = Faker("ko_KR")


class Command(BaseCommand):

    help = "상품 생성"

    def add_arguments(self, parser):
        parser.add_argument("--number", default=2, type=int, help="몇 개의 상품을 만들까요?")

    def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        all_users = user_models.User.objects.all()
        # categories = product_models.Category.objects.all()
        seeder.add_entity(
            product_models.Product,
            number,
            {
                "user": lambda x: random.choice(all_users),
                "category": product_models.Category.objects.get(name="차량"),
                "title": lambda x: seeder.faker.sentence(
                    nb_words=6, variable_nb_words=True, ext_word_list=None
                ),
                "price": lambda x: random.randint(1, 1000) * 1000,
                "created": lambda x: seeder.faker.date_time_between_dates(
                    datetime_start=datetime.now() - timedelta(days=60),
                    datetime_end=datetime.now(),
                ),
            },
        )
        products = seeder.execute()
        products = flatten(list(products.values()))
        for pk in products:
            product = product_models.Product.objects.get(pk=pk)
            product_models.Image.objects.create(
                product=product, image=f"/seed_cars/{random.randint(1, 31)}.jpg",
            )

        self.stdout.write(self.style.SUCCESS(f"{number}개의 상품이 생성되었습니다!"))
