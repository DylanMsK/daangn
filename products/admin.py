from django.contrib import admin
from django.utils.html import mark_safe
from products import models


class ImageInline(admin.TabularInline):
    model = models.Image


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):

    """ Product Admin Definition """

    inlines = (ImageInline,)

    list_display = (
        "user",
        "title",
        "price",
    )
    ordering = ("created",)
    list_filter = ("price",)

    raw_id_fields = ("user",)

    search_fields = (
        "title",
        "^user__username",
        "^user__name",
    )

    def count_images(self, obj):
        return obj.images.count()


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):

    """ Category Admin Definition """

    list_display = ("name",)


@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):

    """ Image Admin Definition """

    list_display = (
        "get_thumbnail",
        "created",
    )

    def get_thumbnail(self, obj):
        return mark_safe(f"<img width='50px' src='{obj.file.url}'/>")

    get_thumbnail.short_description = "썸네일"
