from django.urls import path
from products import views


app_name = "products"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("cars/", views.CarListView.as_view(), name="car_list",),
    path("cars/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("hots/", views.HotListView.as_view(), name="hot_list"),
    path("furnitures/", views.FurnitureListView.as_view(), name="furniture_list"),
    path("children/", views.ChildrenListView.as_view(), name="children_list"),
    path("life/", views.LifeListView.as_view(), name="life_list"),
    path("register/", views.register, name="register"),
]
