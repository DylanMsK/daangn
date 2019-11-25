from django.urls import path
from products import views


app_name = "products"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("car/", views.CategorizedProductView.as_view(), name="categorized_products",),
    path("car/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("register/", views.register, name="register"),
]
