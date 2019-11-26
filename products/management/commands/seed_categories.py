from django.core.management.base import BaseCommand
from products.models import Category


class Command(BaseCommand):

    help = "카테고리 생성"

    def handle(self, *args, **options):
        categories = [
            "차량",
            "인기매물",
            "가구/인테리어",
            "유아동/유아도서",
            "생활/가공식품",
            "기타",
        ]
        for category in categories:
            Category.objects.create(name=category)

        self.stdout.write(self.style.SUCCESS(f"카테고리가 생성되었습니다!"))
