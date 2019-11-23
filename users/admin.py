from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext, gettext_lazy as _
from users import models


# Register your models here.
@admin.register(models.User)
class CustomUserAdmin(UserAdmin):

    """
    Custom User Admin

    관리자 페이지에서 보여지는 사용자 페이지를 커스터마이징한다.
    """

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    list_display = (
        "username",
        "name",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    search_fields = (
        "username",
        "name",
    )
