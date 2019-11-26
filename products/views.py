from django.views import generic
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from products import models, forms
from users import models as user_models


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


class CarListView(generic.View):

    """
    Categorized Product views

    특정 카테고리의 상품 리스트를 보여주는 view
    """

    def get(self, request):
        form = forms.FilterForm(request.GET)
        qs = models.Car.objects.all()
        if form.is_valid():
            min_year = form.cleaned_data.get("min_year")
            max_year = form.cleaned_data.get("max_year")
            min_driven_distance = form.cleaned_data.get("min_driven_distance")
            max_driven_distance = form.cleaned_data.get("max_driven_distance")
            smoking = form.cleaned_data.get("smoking", None)

            filter_args = {}

            filter_args["year__gte"] = min_year

            filter_args["year__lte"] = max_year

            filter_args["driven_distance__gte"] = min_driven_distance

            filter_args["driven_distance__lte"] = max_driven_distance

            if smoking is not None:
                filter_args["smoking"] = smoking
            qs = qs.filter(**filter_args).order_by("-created")
            paginator = Paginator(qs, 12, 6)
            page = request.GET.get("page", 1)
            products = paginator.get_page(page)
            if (
                min_year != 1990
                or max_year != 2020
                or min_driven_distance != 0
                or max_driven_distance != 1000000
                or smoking is not None
            ):
                filtered = True
            else:
                filtered = False
            context = {
                "form": form,
                "products": products,
                "min_year": min_year,
                "max_year": max_year,
                "min_driven_distance": min_driven_distance,
                "max_driven_distance": max_driven_distance,
                "smoking": smoking,
                "filtered": filtered,
            }
        else:
            form = forms.FilterForm()
            qs = qs.order_by("-created")
            paginator = Paginator(qs, 12, 6)
            page = request.GET.get("page", 1)
            products = paginator.get_page(page)
            context = {"form": form, "products": products}
        context["category"] = self.request.path.strip("/")
        return render(request, "products/product_list.html", context)


class ProductDetailView(generic.DetailView):
    """
    Product Detail View
    """

    model = models.Car
    template_name = "products/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["months"] = (timezone.now() - obj.created).days // 30
        context["days"] = (timezone.now() - obj.created).days
        return context


@login_required(login_url="/users/login/")
def register(request):
    form = forms.RegisterProductForm(request.POST, request.FILES, user=request.user)
    if request.method == "POST":
        if form.is_valid():
            instance = form.save()
            if instance.category.name == "차량":
                return redirect("products:product_detail", pk=instance.id)
            else:
                return redirect("products:home")
    else:
        form = forms.RegisterProductForm(user=request.user)
    return render(request, "products/product_create.html", {"form": form})
