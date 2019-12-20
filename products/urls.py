from django.urls import path
from products import views


app_name = "products"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("<int:pk>/", views.ProductDetailView.as_view(), name="product_detail",),
    path("register/", views.register, name="register"),
    path(
        "products/<str:category>/",
        views.CategoryListView.as_view(),
        name="category_list",
    ),
]
