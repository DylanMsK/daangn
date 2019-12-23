from django.urls import path
from products import views


app_name = "products"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("register/", views.register, name="register"),
    path(
        "products/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail",
    ),
    path(
        "products/<str:category>/",
        views.CategoryListView.as_view(),
        name="category_list",
    ),
]
