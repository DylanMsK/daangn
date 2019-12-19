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
    paginate_by = 12  # 페이지당 노출되는 상품 갯수
    paginate_orphans = 6  # 마지막 페이지에 보여줄 최소 상품 갯수
    ordering = "-created"
    context_object_name = "products"
    categories = {
        "car": "차량",
        "hot": "인기매물",
        "furniture": "가구/인테리어",
        "children": "유아동/유아도서",
        "life": "생활/가공식품",
        "etc": "기타",
    }

    def get_queryset(self, category=None):
        queryset = models.Product.objects.all()
        if category is not None:
            for cat_eng, cat_kor in self.categories.items():
                if cat_eng == category:
                    queryset = queryset.filter(category__name=cat_kor)
                    break
            else:
                return redirect("products:home")

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset

    def get_context_data(self, *, queryset=None, **kwargs):
        """Get the context for this view."""

        # 임시 밸리데이션
        if queryset is None:
            print("카테고리가 없음!!")
            print("카테고리가 없음!!")
            print("카테고리가 없음!!")

        page_size = self.paginate_by
        context_object_name = self.context_object_name
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(
                queryset, page_size
            )
            context = {
                "paginator": paginator,
                "page_obj": page,
                "is_paginated": is_paginated,
            }
        else:
            context = {
                "paginator": None,
                "page_obj": None,
                "is_paginated": False,
            }
        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)
        context["categories"] = self.categories
        context["category"] = self.request.GET.get("category")
        return context

    def get(self, request, *args, **kwargs):
        print(request.GET)
        category = request.GET.get("category")
        if category is None:
            queryset = self.get_queryset()
            context = self.get_context_data(queryset=queryset)
            return render(request, "home.html", context)
        else:
            queryset = self.get_queryset(category)
            context = self.get_context_data(queryset=queryset)
            return render(request, "products/product_list.html", context)


class CategoryListView(generic.ListView):
    """
    Categorized Product views

    특정 카테고리의 상품 리스트를 보여주는 view
    """

    def get_queryset(self):
        categories = {
            "car": "차량",
        }
        category = self.kwargs.get("category")
        if categories.get(category):
            return redirect("products:home")
        queryset = models.Product.objects.filter(category_name=categories[category])
        return queryset

    def get(self, request, *args, **kwargs):
        category = kwargs.get("category")
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
        context["page_name"] = "차량"
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
            product = form.save()
            if product.category.name == "차량":
                return redirect("products:product_detail", pk=product.id)
            else:
                return redirect("products:home")
    else:
        form = forms.RegisterProductForm(user=request.user)
    return render(request, "products/product_create.html", {"form": form})


class HotListView(generic.View):
    def get(self, request):
        products = models.Product.objects.filter(category__id=2)
        context = {
            "products": products,
            "page_name": "인기매물",
        }
        return render(request, "products/product_list.html", context)


class FurnitureListView(generic.View):
    def get(self, request):
        products = models.Product.objects.filter(category__id=3)
        context = {
            "products": products,
            "page_name": "가구/인테리어",
        }
        return render(request, "products/product_list.html", context)


class ChildrenListView(generic.View):
    def get(self, request):
        products = models.Product.objects.filter(category__id=4)
        context = {
            "products": products,
            "page_name": "유아동/유아도서",
        }
        return render(request, "products/product_list.html", context)


class LifeListView(generic.View):
    def get(self, request):
        products = models.Product.objects.filter(category__id=2)
        context = {
            "products": products,
            "page_name": "생활/가공식품",
        }
        return render(request, "products/product_list.html", context)
