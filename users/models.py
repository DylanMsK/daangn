from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    """
    Custom User Model

    Django에서 기본 제공하는 AbstractUser 모델의 필드를 상속받아 오버라이드 한다.

    username(string): 로그인시 사용하는 이메일
    password(string): 로그인시 사용하는 패스워드
    is_staff(boolean): 사용자의 staff 권한 유무
    is_active(boolean): 사용자의 활동 유무
    is_superuser(boolean): 최상위 사용자 권한 유무
    date_joined(datetime): 사용자의 가입 날짜
    last_login(datetime): 사용자의 최종 로그인 날짜
    """

    name: str = models.CharField(
        "이름", max_length=72, null=False, blank=True, default=""
    )
    email: str = models.EmailField("이메일", null=False)
