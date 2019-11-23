from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from base import models as base_models
from users import models as user_models


# Create your models here.
class AbstractItem(base_models.TimeStampedModel):

    """
    Abatract Item

    상속받은 TimeStampedModel과 같이 추후 중복적으로 필요한 필드를 정의해 다른 모델에서 상속받는다.
    """

    name: str = models.CharField("이름", max_length=80)

    class meta:
        abstract = True

    def __str__(self):
        return self.name


class Category(AbstractItem):

    """
    Product Category

    등록될 제품들의 카테고리를 정의
    """

    class Meta:
        verbose_name = "카테고리"
        verbose_name_plural = "카테고리"


def set_FK_model_category():
    return Category.objects.get(name="기타")


class Product(base_models.TimeStampedModel):
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
        "가격",
        null=False,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100000000)],
    )

    class Meta:
        verbose_name = "상품"
        verbose_name_plural = "상품"

    def __str__(self):
        return f"{self.user} | {self.title}"


class Image(base_models.TimeStampedModel):
    image = models.ImageField(
        "사진", upload_to="product_images", default="default.png", null=False
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
