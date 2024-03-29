from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from base import models as base_models
from users import models as user_models


# Create your models here.
class Category(base_models.TimeStampedModel):

    """
    Product Category

    등록될 제품들의 카테고리를 정의
    """

    name: str = models.CharField(
        "카테고리명", db_index=True, null=False, unique=True, max_length=30
    )

    class Meta:
        verbose_name = "카테고리"
        verbose_name_plural = "카테고리"

    def __str__(self):
        return self.name


def set_FK_model_category():
    return Category.objects.get(name="기타")


class Product(base_models.TimeStampedModel):

    """
    Product 모델

    모든 상품에 공통적으로 필요한 필드들을 정의
    """

    user: user_models.User = models.ForeignKey(
        user_models.User,
        on_delete=models.CASCADE,
        related_name="products",
        null=False,
        verbose_name="유저",
    )
    category: Category = models.ForeignKey(
        Category,
        on_delete=models.SET(set_FK_model_category),
        related_name="products",
        null=False,
        verbose_name="카테고리",
    )
    title: str = models.CharField("제목", max_length=120, null=False)
    price: int = models.PositiveIntegerField(
        "가격(원)",
        null=False,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100000000)],
    )
    describe: str = models.TextField("설명", null=False)

    class Meta:
        verbose_name = "상품"
        verbose_name_plural = "상품"

    def __str__(self):
        return f"{self.title}"

    def count_images(self):
        return self.images.count()

    count_images.short_description = "이미지 갯수"


class Image(base_models.TimeStampedModel):
    """
    Image 모델

    상품에 등록될 사진들을 저장하는 테이블
    """

    image = models.ImageField(
        "사진", upload_to="product_images/", default="default.png", null=False
    )
    product: Product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        null=False,
        verbose_name="상품",
    )

    class Meta:
        verbose_name = "사진"
        verbose_name_plural = "사진"


class Car(Product):
    """
    Car 모델

    차량 카테고리의 상품들을 저장하는 테이블
    """

    MIN_YEAR = 1900
    MIN_DRIVEN_DISTANCE = 0
    MAX_DRIVEN_DISTANCE = 10000000

    year: int = models.PositiveIntegerField(
        "연식(년)", db_index=True, null=False, validators=[MinValueValidator(MIN_YEAR)],
    )
    driven_distance: int = models.PositiveIntegerField(
        "주행 거리(km)",
        db_index=True,
        null=False,
        default=0,
        validators=[
            MinValueValidator(MIN_DRIVEN_DISTANCE),
            MaxValueValidator(MAX_DRIVEN_DISTANCE),
        ],
    )
    smoking: bool = models.BooleanField("흡연 여부", null=False, default=False)

    class Meta:
        verbose_name = "차량"
        verbose_name_plural = "차량"

    def __str__(self):
        return self.title
