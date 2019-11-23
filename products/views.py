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
