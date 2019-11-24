from django.contrib import admin
from django.utils.html import mark_safe
from products import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):

    """ Category Admin Definition """

    list_display = (
        "name",
        "count_category",
    )
    search_fields = ("name",)
    list_filter = ("name",)

    def count_category(self, obj):
        return obj.products.count()

    count_category.short_description = "상품 갯수"


class ImageInline(admin.TabularInline):
    model = models.Image


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):

    """ Product Admin Definition """

    inlines = (ImageInline,)

    list_display = (
        "title",
        "user",
        "category",
        "price",
        "count_images",
    )
    ordering = ("created",)

    list_filter = ("category",)

    raw_id_fields = ("user",)

    search_fields = (
        "title",
        "^user__username",
        "^user__name",
    )


@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):

    """ Image Admin Definition """

    list_display = (
        "get_thumbnail",
        "created",
    )
    search_fields = (
        "products__user__username",
        "products__user__name",
    )

    def get_thumbnail(self, obj):
        return mark_safe(f"<img width='50px' src='{obj.image.url}'/>")

    get_thumbnail.short_description = "썸네일"


@admin.register(models.Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "price",
        "year",
        "driven_distance",
        "smoking",
        "count_images",
    )
    list_filter = (
        "year",
        "smoking",
    )
