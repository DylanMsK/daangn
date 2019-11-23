from django.urls import path
from products import views


app_name = "base"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
]
