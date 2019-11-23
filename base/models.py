from django.db import models


# Create your models here.
class TimeStampedModel(models.Model):

    """
    Time Stamped Model

    모델별로 중복적으로 들어갈 필드를 정의 한다.
    추후 생성되는 모델에서 이 모델을 상속받는다.
    """

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
