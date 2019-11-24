from django.views import generic
from django.shortcuts import render
from django.core.paginator import Paginator
from products import models


# Create your views here.
class HomeView(generic.ListView):

    """
    HomeView Definition
    
    메인페이지에서 상품들의 리스트를 보여주는 view
    """

    model = models.Product
    template_name = "home.html"
    paginate_by = 12
    paginate_orphans = 6
    ordering = "-created"
    context_object_name = "products"


class CategorizedProductView(generic.ListView):

    """
    Categorized Product views

    특정 카테고리의 상품 리스트를 보여주는 view
    """

    model = models.Car
    template_name = "products/product_list.html"
    paginate_by = 12
    paginate_orphans = 6
    ordering = "-created"
    context_object_name = "products"

    def get_queryset(self):
        category = self.request.path.strip("/")
        category_name = {"car": "차량"}
        return models.Car.objects.filter(category__name=category_name[category])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.request.path.strip("/")
        return context


class ProductDetailView(generic.DetailView):

    """
    Product Detail View
    """

    model = models.Car
    template_name = "products/product_detail.html"
    context_object_name = "product"
