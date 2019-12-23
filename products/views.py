from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import Http404
from django.db.models import Prefetch
from products import models, forms, filters
from users import models as user_models


CATEGORY_DICT = {
    "car": "차량",
    "hot": "인기매물",
    "furniture": "가구/인테리어",
    "children": "유아동/유아도서",
    "life": "생활/가공식품",
    "etc": "기타",
}


# Create your views here.
class HomeView(generic.ListView):
    """
    HomeView Definition

    메인페이지에서 상품들의 리스트를 보여주는 view
    """

    model = models.Product
    paginate_by = 12  # 페이지당 노출되는 상품 갯수
    ordering = "-created"

    def get_queryset(self):
        # queryset = models.Product.objects.all()
        # queryset = models.Product.objects.select_related("category").all()
        queryset = (
            models.Product.objects.prefetch_related(
                Prefetch("images", queryset=models.Image.objects.all(), to_attr="image")
            )
            .select_related("category")
            .all()
        )

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        """Get the context for this view."""
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset, self.paginate_by
        )
        context = {
            "paginator": paginator,
            "page_obj": page,
            "is_paginated": is_paginated,
            "products": queryset,
            "categories": CATEGORY_DICT,
        }
        context.update(kwargs)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, "home.html", context)


class CategoryListView(generic.ListView):
    """
    Categorized Product views

    특정 카테고리의 상품 리스트를 보여주는 view
    """

    paginate_by = 12
    ordering = "-created"

    def get_queryset(self, category=None, filter_args=None):
        if category == "차량":
            queryset = models.Car.objects.all()
            queryset = (
                models.Car.objects.prefetch_related(
                    Prefetch(
                        "images", queryset=models.Image.objects.all(), to_attr="image"
                    )
                )
                .select_related("category")
                .all()
            )
            if filter_args is not None:
                filter_args = filters.ProductFilter(filter_args).car_filter()
                queryset = queryset.filter(**filter_args)
        else:
            queryset = (
                models.Product.objects.prefetch_related(
                    Prefetch(
                        "images", queryset=models.Image.objects.all(), to_attr="image"
                    )
                )
                .select_related("category")
                .all()
            )

            for cat_eng, cat_kor in CATEGORY_DICT.items():
                if cat_kor == category:
                    queryset = queryset.filter(category__name=cat_kor)
                    break

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        """Get the context for this view."""

        paginator, page, queryset, is_paginated = self.paginate_queryset(
            object_list, self.paginate_by
        )
        context = {
            "paginator": paginator,
            "page_obj": page,
            "is_paginated": is_paginated,
            "products": queryset,
            "category": {
                "eng_name": self.kwargs.get("category"),
                "kor_name": CATEGORY_DICT.get(self.kwargs.get("category")),
            },
        }
        context.update(kwargs)
        return context

    def get(self, request, *args, **kwargs):
        category = CATEGORY_DICT.get(kwargs.get("category"))
        if category is None:
            return redirect("products:home")
        else:
            form = forms.FilterForm(request.GET)
            if form.is_valid():
                queryset = self.get_queryset(
                    category=category, filter_args=form.cleaned_data
                )
                context = self.get_context_data(object_list=queryset)
            else:
                queryset = self.get_queryset(category)
                context = self.get_context_data(object_list=queryset)
            context["form"] = form
            context.update(**form.cleaned_data)
            return render(request, "products/product_list.html", context)


class ProductDetailView(generic.DetailView):
    """
    Product Detail View
    """

    # model = models.Product
    template_name = "products/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        queryset = (
            models.Product.objects.prefetch_related(
                Prefetch("images", queryset=models.Image.objects.all(), to_attr="image")
            )
            .select_related("category")
            .all()
        )
        return queryset

    def get_object(self, pk):
        queryset = self.get_queryset()
        product = get_object_or_404(queryset, pk=pk)
        if product.category.name == "차량":
            try:
                product = models.Car.objects.get(product_ptr=product)
            except models.Car.DoesNotExists:
                return Http404()
        return product

    def get_context_data(self, **kwargs):
        context = {}
        product = kwargs.get("object")
        context[self.context_object_name] = product
        context["months"] = (timezone.now() - product.created).days // 30
        context["days"] = (timezone.now() - product.created).days
        return context

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        if pk is None:
            return redirect("products:home")
        product = self.get_object(pk)
        context = self.get_context_data(object=product)
        return self.render_to_response(context)


@login_required(login_url="/users/login/")
def register(request):
    if request.method == "POST":
        form = forms.RegisterProductForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            product = form.save()
            return redirect("products:product_detail", pk=product.id)
    elif request.method == "GET":
        form = forms.RegisterProductForm(user=request.user)
        return render(request, "products/product_create.html", {"form": form})
    else:
        return redirect("products:home")
