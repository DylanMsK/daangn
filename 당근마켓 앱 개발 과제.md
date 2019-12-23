# [Feedback 반영] 당근마켓 웹 개발 과제



## 참고 링크

#### !! Heroku에 배포하였기 때문에 첫 접속시 지연시간이 있을 수 있습니다 !!

- 배포 버전: [https://daangn.herokuapp.com/](https://daangn.herokuapp.com/)

- 관리자 페이지: [https://daangn.herokuapp.com/admin/](https://daangn.herokuapp.com/admin/)

  - Id: admin

  - Password: admin

- 깃헙:  https://github.com/DylanMsK/daangn





## 피드백 반영

### 프론트엔드

##### 1. 서버로부터 받은 에러(5xx, 4xx 등)에 대해 처리를 하는가?

django.conf.ulrs 모듈에 내장되어 있는 함수를 오버라이드 해서 에러 핸들링을 적용.

```python
# config/urls.py
from django.conf.urls import handler400, handler404, handler500

handler400 = "base.views.error400"
handler404 = "base.views.error404"
handler500 = "base.views.error500"


# base/views.py
def error400(request, exception):
    return render(request, "404.html", status=400)


def error404(request, exception):
    return render(request, "404.html", status=404)


def error500(request):
    return render(request, "500.html", status=500)
```



### 백엔드

##### 2. 보안에 취약한 쿼리(예: SQL Injection)가 발생하지 않도록 처리를 하는가? 

DB 조회와 생성 등의 쿼리가 발생하는 모든곳에 SQL Injection을 고려합니다.

**[products/views.py](https://github.com/DylanMsK/daangn/blob/master/products/views.py)**

```python
# 클라이언트는 허가된 카테고리만 조회 가능합니다.

CATEGORY_DICT = {
    "car": "차량",
    "hot": "인기매물",
    "furniture": "가구/인테리어",
    "children": "유아동/유아도서",
    "life": "생활/가공식품",
    "etc": "기타",
}

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
```



**[products/validators.py](https://github.com/DylanMsK/daangn/blob/master/products/validators.py)**

```python
# 카테고리별 정해진 필드만 DB에 입력 받고 이 외의 데이터는 삭제합니다.

GENERAL_FIELDS = ["user", "image", "title", "category", "price", "describe"]
CAR_FIELDS = ["year", "driven_distance", "smoking"]
LEGACY_FIELDS = []

def delete_wrong_fields(self, category):
  if category.name == "차량":
    for field in self.GENERAL_FIELDS + self.CAR_FIELDS:
      self.cleaned_data[field] = self.data[field]

      else:
        for field in self.GENERAL_FIELDS + self.LEGACY_FIELDS:
          self.cleaned_data[field] = self.data[field]
```



##### 3. RESTful하게 URI와 method를 사용하고 있는가?

상품을 조회하고 생성하는 URL을 직관적으로 변경하고 HTTP 메소드별 CRUD 로직을 적용

이번 프로젝트에서는 Django Rest Framework(DRF) 모델이 아닌 Model Template View(MTV) 모델을 사용해 Django 풀스택으로 작업했기 때문에 완성도 높은 REST 구조를 따르지 못했습니다. 하지만 허가하지 않은 HTTP method로 접근시 에러를 발생시켜 안정도를 높혔습니다.

**[products/urls.py](https://github.com/DylanMsK/daangn/blob/master/products/urls.py)**

```python
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
```



**[products/views.py](https://github.com/DylanMsK/daangn/blob/master/products/views.py)**

```python
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
```



##### 4. 데이터를 가져올 때 성능(예: N+1 쿼리 처리)을 고려했는가?

Django ORM이 제공하는 쿼리 최적화 메소드를 사용해 중복되는 쿼리와 유사한 쿼리를 제거해 성능을 높혔습니다.

##### 수정 전

메인 페이지에서 모든 상품 리스트를 조회할 시 `models.Product.objects.all()` 을 사용해 **총 26개의 쿼리문을 사용**합니다. 이 중 24개의 유사한 쿼리가 있고 12개의 중복 쿼리가 포함되어 있으며 총 시간은 **4.23ms**가 소요되었습니다.

```python
# products/views.py
def get_queryset(self):
    queryset = models.Product.objects.all()
    return queryset
```

![수정 전](/Users/dylan/Desktop/github/daangn/readme/img/수정 전.png)



##### 수정 1

상품 당 카테고리가 1:N 관계로 잡혀있기 때문에 상품에 카테고리 이름 정보를 조인해 카테고리를 다시 조회하는 중복쿼리를 제거했습니다. 결과적으로 26개의 **쿼리가 14개로 줄어**들었고 총 시간은 **1.96ms**로 줄었습니다.

```python
def get_queryset(self):
    queryset = models.Product.objects.select_related("category").all()
    return queryset
```

![카테고리 조인](/Users/dylan/Desktop/github/daangn/readme/img/카테고리 조인.png)



##### 수정 2

상품 정보에 카테고리를 조인한 것과 마찬가지로 상품당 이미지 정보도 조인을 해 유사한 쿼리를 제거했습니다. 결과적으로 26개의 **쿼리가 3개로 줄어**들었고 총 시간은 **0.83ms** 로 줄었습니다.

```python
def get_queryset(self):
    queryset = (
      models.Product.objects.prefetch_related(
        Prefetch("images", queryset=models.Image.objects.all(), to_attr="image")
      )
      .select_related("category")
      .all()
    )
  return queryset
```

![이미지 조인](/Users/dylan/Desktop/github/daangn/readme/img/이미지 조인.png)



### 데이터베이스

##### 5. 성능을 고려하여 인덱스를 추가했는가?

카테고리 테이블의 **카테고리 이름** 필드와 **차량 연식**, **차량 주행거리** 필드에 추가적인 인덱스를 주었습니다. 명세에는 차량 이외의 카테고리에 대한 필터링 조건은 없었기 때문에 차량 테이블에만 인덱스를 주었습니다.

결과적으로 `Category`, `Product`, `Car`, `Image` 테이블의 SQL은 아래와 같습니다.

```sql
BEGIN;
--
-- Create model Category
--
CREATE TABLE "products_category" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created" datetime NOT NULL, "updated" datetime NOT NULL, "name" varchar(30) NOT NULL);
--
-- Create model Product
--
CREATE TABLE "products_product" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created" datetime NOT NULL, "updated" datetime NOT NULL, "title" varchar(120) NOT NULL, "price" integer unsigned NOT NULL CHECK ("price" >= 0), "describe" text NOT NULL, "category_id" integer NOT NULL REFERENCES "products_category" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" integer NOT NULL REFERENCES "users_user" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Car
--
CREATE TABLE "products_car" ("product_ptr_id" integer NOT NULL PRIMARY KEY REFERENCES "products_product" ("id") DEFERRABLE INITIALLY DEFERRED, "year" integer unsigned NOT NULL CHECK ("year" >= 0), "driven_distance" integer unsigned NOT NULL CHECK ("driven_distance" >= 0), "smoking" bool NOT NULL);
--
-- Create model Image
--
CREATE TABLE "products_image" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created" datetime NOT NULL, "updated" datetime NOT NULL, "image" varchar(100) NOT NULL, "product_id" integer NOT NULL REFERENCES "products_product" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "products_category_name_0ecfb368" ON "products_category" ("name");
CREATE INDEX "products_product_category_id_9b594869" ON "products_product" ("category_id");
CREATE INDEX "products_product_user_id_e04f062e" ON "products_product" ("user_id");
CREATE INDEX "products_car_year_87247a66" ON "products_car" ("year");
CREATE INDEX "products_car_driven_distance_27926a9b" ON "products_car" ("driven_distance");
CREATE INDEX "products_image_product_id_978188e9" ON "products_image" ("product_id");
COMMIT;
```



##### 6. column의 속성(예: nullable) 및 constraint(예: unique)을 지정했는가?

`Category` 테이블의 카테고리 이름 필드에 null, unique 옵션을 주었습니다.

```python
class Category(base_models.TimeStampedModel):
    name: str = models.CharField(
        "카테고리명", db_index=True, null=False, unique=True, max_length=30
    )
```



### 기타

##### 7. 중복된 코드를 모듈/파일로 분리하여 처리를 하는가?

사용자가 입력한 **폼을 validation하는 로직을 별도 묘듈로 분리**하였습니다. 상품 카테고리 **필터링 조건 또한 별도 모듈로 분리**해였고 **추후 확장 가능성을 고려해 필터링 클래스를 작성**했습니다.

**[products/validators.py](https://github.com/DylanMsK/daangn/blob/master/products/validators.py)**

```python
import re
from datetime import datetime
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from products import models as product_models
from users import models as user_models


class ProductRegisterValidator:
    """
    상품 등록시 폼 작성 유효성 검사
    """

    GENERAL_FIELDS = ["user", "image", "title", "category", "price", "describe"]
    CAR_FIELDS = ["year", "driven_distance", "smoking"]
    LEGACY_FIELDS = []

    def __init__(self, user, data):
        self.user = user
        self.data = data
        self.cleaned_data = {}
        self.errors = []

    def delete_wrong_fields(self, category):

        if category.name == "차량":
            for field in self.GENERAL_FIELDS + self.CAR_FIELDS:
                self.cleaned_data[field] = self.data[field]

        else:
            for field in self.GENERAL_FIELDS + self.LEGACY_FIELDS:
                self.cleaned_data[field] = self.data[field]

    def general_validate(self):
        """
        공통된 필드 유효성 평가
        """
        image = self.data.get("image")
        title = self.data.get("title")
        category = self.data.get("category")
        price = self.data.get("price")
        describe = self.data.get("describe")

        # 로그인된 사용자 체크
        if not user_models.User.objects.filter(id=self.user.id).exists():
            self.errors.append((None, "로그인된 사용자만 판매글을 작성할 수 있습니다."))
        else:
            self.data["user"] = user_models.User.objects.get(id=self.user.id)

        # 이미지 업로드 체크
        content_type = image.content_type.split("/")[0]
        if content_type in settings.CONTENT_TYPES:
            if image.size > settings.MAX_UPLOAD_SIZE:
                self.errors.append(
                    (
                        "image",
                        "10MB 이하의 이미지만 업로드할 수 있습니다. 현재 파일 용량: %s"
                        % filesizeformat(image.size),
                    )
                )
        else:
            self.errors.append(("image", "이미지 파일만 첨부할 수 있습니다."))

        # 제목 입력 체크
        if title is None:
            self.errors.append(("title", "제품 이름을 입력해주세요."))

        # 카테고리 선택 체크
        if category is None or category == 0:
            self.errors.append(("category", "카테고리를 선택해주세요."))

        # 가격 입력 체크
        if price is None:
            self.errors.append(("price", "가격을 입력해주세요. (￦)"))
        else:
            if price < 0 or price > 100000000:
                self.errors.append(("price", "1억원 이하의 금액만 등록 가능합니다."))

        # 설명 입력 체크
        if describe is None:
            self.errors.append(("describe", "제품 설명을 작성해주세요."))

    def car_validate(self):
        year = self.data.get("year")
        driven_distance = self.data.get("driven_distance")
        smoking = self.data.get("smoking")

        # 연식 체크
        if year is None:
            self.errors.append(("year", "차량 연식을 선택해주세요."))
        elif year < 1990 or year > 2020:
            self.errors.append(("year", "1990년에서 2020년 사이에 제작된 차량만 등록 가능합니다."))

        # 주행 거리 체크
        if driven_distance is None or driven_distance == "":
            self.errors.append(("driven_distance", "주행거리를 입력해주세요.(km)"))
        elif driven_distance < 0 or driven_distance > 100000:
            self.errors.append(
                ("driven_distance", "주행거리가 0km에서 100,000km 까지의 차량만 등록 가능합니다.")
            )

        # 흡연 유무 체크
        if smoking is None or smoking == "":
            self.errors.append(("smoking", "흡연유무를 선택해 주세요."))

    def check(self):
        self.general_validate()
        category_pk = self.data.get("category")
        try:
            category = product_models.Category.objects.get(pk=category_pk)
            self.data["category"] = category
        except product_models.Category.DoesNotExists:
            return None, self.errors

        if category.name == "차량":
            self.car_validate()
        # 다른 카테고리 유효성 검사
        elif category.name == "something":
            pass
        self.delete_wrong_fields(category)
        return self.cleaned_data, None


class ProductFilterValidator:
    def __init__(self, data):
        self.data = data
        self.cleaned_data = {}

    def car_validate(self):
        year = self.data.get("year")
        driven_distance = self.data.get("driven_distance")
        smoking = self.data.get("smoking")

        # 연식 체크
        default_min_year = product_models.Car.MIN_YEAR
        default_max_year = datetime.now().year
        if year is not None and re.match("^[\d]+,[\d]+$", year):
            min_year, max_year = map(int, year.split(","))
            if default_min_year <= min_year <= default_max_year:
                self.cleaned_data["min_year"] = min_year
            else:
                self.cleaned_data["min_year"] = default_min_year

            if default_min_year <= max_year <= default_max_year:
                self.cleaned_data["max_year"] = max_year
            else:
                self.cleaned_data["max_year"] = default_max_year
        else:
            self.cleaned_data["min_year"] = default_min_year
            self.cleaned_data["max_year"] = default_max_year

        # 주행거리 체크
        default_min_distance = product_models.Car.MIN_DRIVEN_DISTANCE
        default_max_distance = product_models.Car.MAX_DRIVEN_DISTANCE
        if driven_distance is not None and re.match("^[\d]+,[\d]+$", driven_distance):
            min_distance, max_distance = map(int, driven_distance.split(","))
            if default_min_distance <= min_distance <= default_max_distance:
                self.cleaned_data["min_driven_distance"] = min_distance
            else:
                self.cleaned_data["min_driven_distance"] = default_min_distance

            if default_min_distance <= max_distance <= default_max_distance:
                self.cleaned_data["max_driven_distance"] = max_distance
            else:
                self.cleaned_data["max_driven_distance"] = default_max_distance

        else:
            self.cleaned_data["min_driven_distance"] = default_min_distance
            self.cleaned_data["max_driven_distance"] = default_max_distance

        # 흡연유무 체크
        if smoking in ["total", True, False]:
            self.cleaned_data["smoking"] = smoking
        else:
            self.cleaned_data["smoking"] = "total"

    def check(self):
        self.car_validate()
        return self.cleaned_data
```



**[products/filters.py](https://github.com/DylanMsK/daangn/blob/master/products/filters.py)**

```python
from datetime import datetime
from products import models


class ProductFilter:
    def __init__(self, filter_args):
        self.filter_args = filter_args

    def general_filter(self):
        pass

    def car_filter(self):
        min_year = self.filter_args.get("min_year")
        max_year = self.filter_args.get("max_year")
        min_distance = self.filter_args.get("min_driven_distance")
        max_distance = self.filter_args.get("max_driven_distance")
        smoking = self.filter_args.get("smoking")

        filter_args = {}

        if min_year is not None:
            filter_args["year__gte"] = min_year
        else:
            filter_args["year__gte"] = models.Car.MIN_YEAR

        if max_year is not None:
            filter_args["year__lte"] = max_year
        else:
            filter_args["year__lte"] = datetime.now().year

        if min_distance is not None:
            filter_args["driven_distance__gte"] = min_distance
        else:
            filter_args["driven_distance__gte"] = models.Car.MIN_DRIVEN_DISTANCE

        if max_distance is not None:
            filter_args["driven_distance__lte"] = max_distance
        else:
            filter_args["driven_distance__lte"] = models.Car.MAX_DRIVEN_DISTANCE
        if smoking is not None:
            if smoking != "total":
                filter_args["smoking"] = smoking

        return filter_args
```



##### 8. 하드코딩 없이 확장성을 고려하여 구현했는가?

카테고리별로 별도 컨트롤러를 만든 이전의 코드를 하나로 통합해 모든 카테고리별 리스트를 조회하는 하나의 컨트롤러로 구현했습니다. 또한 확장성을 고려해 카테고리별 필터링 조건을 별도 모듈로 분리했습니다.

**[products/views.py](https://github.com/DylanMsK/daangn/blob/master/products/views.py)**

```python
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

```



##### 9. 차량 외에는 상품이 등록되지 않아 감점합니다. (-20)

차량 이외의 카테고리도 정상적으로 등록되게 구현하였고, 카테고리별 validation을 담당하는 로직을 별도 모듈로 분리([products/validators.py](https://github.com/DylanMsK/daangn/blob/master/products/validators.py))하고 중복 코드를 제거함과 동시에 확장성을 고려해 구현했습니다. 



## 개발 환경

- Python 3.6.7
- Heroku
- AWS S3
- Github

##### 과제 진행시 사용한 라이브러리 리스트

```
appdirs==1.4.3
attrs==19.3.0
boto3==1.10.28
botocore==1.13.28
Click==7.0
dj-database-url==0.5.0
Django==2.2.7
django-mathfilters==0.4.0
django-seed==0.1.9
django-storages==1.8
docutils==0.15.2
entrypoints==0.3
Faker==2.0.4
gunicorn==20.0.3
jmespath==0.9.4
mccabe==0.6.1
pathspec==0.6.0
Pillow==6.2.1
psycopg2-binary==2.8.4
python-dateutil==2.8.0
pytz==2019.3
regex==2019.11.1
s3transfer==0.2.1
six==1.13.0
sqlparse==0.3.0
text-unidecode==1.3
toml==0.10.0
typed-ast==1.4.0
urllib3==1.25.7
whitenoise==4.1.4
```



## 프로젝트 구조

### 1. 사용자 로직 담당 [[링크](https://github.com/DylanMsK/daangn/tree/master/users)]

```
daangn/
    ...
    users/
        management/					# seed data 생성
        migrations/					# 사용자 모델 schema
        static/css/					# 사용자 로직에 관련된 페이지의 정적 파일 폴더 
    admin.py						# 사용자 정보들을 관리하는 관리자페이지 커스터마이징
    forms.py						# 로그인/회원가입 등 사용자 폼의 유효성 검사
    models.py						# 사용자 모델 정의
    tests.py						# 사용자 기능별 로직 테스트
    urls.py							# 사용자 URL 경로
    views.py						# 사용자 로직 컨트롤러
    ...
```



### 2. 상품 로직 담당 [[링크](https://github.com/DylanMsK/daangn/tree/master/products)]

```
daangn/
    ...
    products/
        management/					# seed data 생성
        migrations/					# 상품 모델 schema
        static/css/					# 상품 로직에 관련된 페이지의 정적 파일 폴더 
    admin.py						# 상품 정보들을 관리하는 관리자페이지 커스터마이징
    forms.py						# 판매글 작성 및 필터링 폼의 유효성 검사
    models.py						# 상품 모델 정의
    tests.py						# 상품 기능별 로직 테스트
    urls.py							# 상품 URL 경로
    views.py						# 상품 로직 컨트롤러
    ...
```





## 모델 설계

### 1. 사용자 모델 [[링크](https://github.com/DylanMsK/daangn/blob/master/users/models.py)]

사용자 정보를 관리하는 모델은 Django에서 기본 제공하는 `AbstractUser` 모델을 상속받아 오버라이딩하여 설계

```python
class User(AbstractUser):
    """
    Custom User Model

    Django에서 기본 제공하는 AbstractUser 모델의 필드를 상속받아 오버라이드 한다.

    username(string): 로그인시 사용하는 이메일
    password(string): 로그인시 사용하는 패스워드
    is_staff(boolean): 사용자의 staff 권한 유무
    is_active(boolean): 사용자의 활동 유무
    is_superuser(boolean): 최상위 사용자 권한 유무
    date_joined(datetime): 사용자의 가입 날짜
    last_login(datetime): 사용자의 최종 로그인 날짜
    """

    name: str = models.CharField(
        "이름", max_length=72, null=False, blank=True, default=""
    )
    email: str = models.EmailField("이메일", null=False)
```



### 2. 상품 모델 [[링크](https://github.com/DylanMsK/daangn/blob/master/products/models.py)]



```python
class TimeStampedModel(models.Model):
    """
    Time Stamped Model

    모델별로 중복적으로 들어갈 필드를 정의 한다.
    추후 생성되는 모델은 모두 이 모델을 상속받는다.
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Category(base_models.TimeStampedModel):
    """
    Product Category

    등록될 제품들의 카테고리를 정의
    """
    name: str = models.CharField("카테고리명", max_length=30)


class Product(base_models.TimeStampedModel):
    """
    Product 모델

    모든 상품에 공통적으로 필요한 필드들을 정의
    """
    user: user_models.User = models.ForeignKey(
        user_models.User,
        on_delete=models.CASCADE,
        related_name="products",
        null=False,
        verbose_name="유저",
    )
    category: Category = models.ForeignKey(
        Category,
        on_delete=models.SET(set_FK_model_category),
        related_name="products",
        null=False,
        verbose_name="카테고리",
    )
    title: str = models.CharField("제목", max_length=120, null=False)
    price: int = models.PositiveIntegerField(
        "가격(원)",
        null=False,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100000000)],
    )
    describe: str = models.TextField("설명", null=False)
      
      
class Image(base_models.TimeStampedModel):
    """
    Image 모델

    상품에 등록될 사진들을 저장하는 테이블
    """
    image = models.ImageField(
        "사진", upload_to="product_images", default="default.png", null=False
    )
    product: Product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        null=False,
        verbose_name="상품",
    )
      
     
class Car(Product):
	  """
    Car 모델

    차량 카테고리의 상품들을 저장하는 테이블
    """
    year: int = models.PositiveIntegerField("연식(년)", null=False)
    driven_distance: int = models.PositiveIntegerField(
        "주행 거리(km)",
        null=False,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10000000)],
    )
    smoking: bool = models.BooleanField("흡연 여부", null=False, default=False)
```





## 이슈

### 1. 사용자가 회원가입시 이름 필드 부재(해결)

스켈레톤상의 DB 스키마를 보면 name을 입력받게 되어있지만 `signup.html` 상에는 이름을 입력받는 `input tag` 가 없음.
따라서 users 모델의 name 필드에 null 값은 허용하지 않지만 빈 스트링을 등록 가능하게 변경하고, 회원가입시 이름 입력은 선택사항으로 변경



### 2. Product Model Schema(해결)

기존의 상품들은 제목, 카테고리, 가격, 이미지, 상품 등록자 필드로 충분했지만 차량의 카테고리에는 연식, 주행거리, 흡연 여부 등이 추가된다.

또한, 향후 추가될 부동산, 도서 등의 다양한 카테고리가 추가될 것을 고려하여 DB를 설계해야 한다.



> 아래 모델별 장단점을 종합적으로 고려해본 결과 **[5번 Concrete Base Model]** 방법을 통해 DB를 설계한다.



#### 1. Naive Model

가장 간단한 중고 마켓 DB 모델링은 다음과 같을것이다.
```python
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from base import models as base_models
from users import models as user_models


class Category(base_models.TimeStampedModel):
    name = models.CharField(max_length=30)


class Product(base_models.TimeStampedModel):
    title: str = models.CharField(max_length=120)
    price: int = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100000000)],
    )
    category: Category = models.ForeignKey(
        Category,
        on_delete=models.SET(lambda x: Category.objects.get(name="기타")),
        related_name="products",
    )
    user: user_models.User = models.ForeignKey(
        user_models.User, on_delete=models.CASCADE, related_name="products"
    )
    describe: str = models.TextField("설명", null=False)
```

이미 등록된 카테고리 상품에는 공통적인 속성만 필요하므로 위 schema로 모든 상품을 등록할 수 있다.



##### 장점
- 코드의 이해가 쉽고 유지보수가 쉽다.

##### 단점
- 상품 정보에 대한 추가 정보를 저장할 수 없다



#### 2. Sparse Model

1번의 Naive 모델에서 `연식`, `주행거리`, `흡연유무` 필드를 추가해 카테고리를 확장한다.

```python
from datetime import datetime
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from base import models as base_models
from users import models as user_models


class Category(base_models.TimeStampedModel):
    name = models.CharField(max_length=30)


class Product(base_models.TimeStampedModel):
    # 공통 속성
    title: str = models.CharField(max_length=120)
    price: int = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100000000)],
    )
    category: Category = models.ForeignKey(
        Category,
        on_delete=models.SET(lambda x: Category.objects.get(name="기타")),
        related_name="products",
    )
    user: user_models.User = models.ForeignKey(
        user_models.User, on_delete=models.CASCADE, related_name="products"
    )
   	describe: str = models.TextField("설명", null=False)
      
    # 추가 속성
    year: int = models.PositiveIntegerField(
        null=True,
        validators=[MinValueValidator(1900), MaxValueValidator(datetime.now().year)],
    )
    driven_distance: int = models.PositiveIntegerField(
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(10000000)]
    )
    smoking = models.NullBooleanField()
```

추가적인 속성이 필요한 카테고리를 위해 상품 모델에 Null 값을 허용하는 속성을 추가한다.



##### 장점
- 코드의 이해가 쉽고 유지보수가 쉽다.

##### 단점
- 데이터 무결성 원칙 위배된다.
- 특정 카테고리에 대한 Null 값 유무를 확인하기 위해 카테고리별로 유효성 검사를 별도로 진행해야 한다.
- 새로운 카테고리가 추가될 때마다 Schema를 변경해야 한다.
- 결과적으로 빈 값이 많은 DB를 갖게 된다.



#### 3. Semi-Structured Model

공통적으로 사용되는 필드를 제외한 나머지 필드는 하나의 속성으로 저장

```python
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.postgres.fields import JSONField
from base import models as base_models
from users import models as user_models


class Category(base_models.TimeStampedModel):
    name = models.CharField(max_length=30)


class Product(base_models.TimeStampedModel):
    # 공통 속성
    title: str = models.CharField(max_length=120)
    price: int = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100000000)],
    )
    category: Category = models.ForeignKey(
        Category,
        on_delete=models.SET(lambda x: Category.objects.get(name="기타")),
        related_name="products",
    )
    user: user_models.User = models.ForeignKey(
        user_models.User, on_delete=models.CASCADE, related_name="products"
    )
    describe: str = models.TextField("설명", null=False)
      
    # 추가 속성
    extra: dict = JSONField(null=True)
```

Django의 postgres 모듈에서 제공하는 `JSONField`를 사용해 추가적인 속성은 아래 예시와 같이 extra 필드에 저장한다.

```bash
>>> car = Product.objects.create(
        title="티볼리 1인신조차량 무사고 판매해요",
        price=8500000,
        category=Category.objects.get(name="차량"),
        user=User.objects.first(),
        extra={
            "year": 2016,
            "driven_distance": 100000,
            "smoking": True
        }
    )
>>> car.clean()
>>> car
<Product: 티볼리 1인신조차량 무사고 판매해요>
```

먼저 `JSONField`는 PostgreSQL DB에서 제공한다. 다른 데이터베이스에서는 이 기능을 제공하지 않기 때문에 이 방법은 사용할 수 없다. 또한 JSONField 의 경우  필드의 값을 쿼리하고 인덱싱 하는 기능이 제대로 지원되지 않기 때문에 굳이 이 방법을 사용할 바에야 NoSQL을 사용하는 것이 좋다.



##### 장점
- 레코드별로 수많은 빈 필드가 생성되는 것을 방지할 수 있다.
- 새로운 속성을 추가하기 쉽다.

##### 단점
- JSONField를 제공하는 데이터베이스에서만 사용 가능하다.
- JSONField 내부에는 Schema를 정의할 수 없어 유효성 검사가 힘들어진다.



#### 4. Abstract Base Model

공통적으로 사용되는 속성을 가진 Product 모델을 추상화 하고 카테고리 별로 새로운 모델을 정의한다.

```python
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from base import models as base_models
from users import models as user_models


class Category(base_models.TimeStampedModel):
    name = models.CharField(max_length=30)


class Product(base_models.TimeStampedModel):
    class Meta:
        abstract = True

    title: str = models.CharField(max_length=120)
    price: int = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100000000)],
    )
    category: Category = models.ForeignKey(
        Category,
        on_delete=models.SET(lambda x: Category.objects.get(name="기타")),
        related_name="products",
    )
    user: user_models.User = models.ForeignKey(
        user_models.User, on_delete=models.CASCADE, related_name="products"
    )
		describe: str = models.TextField("설명", null=False)
      

class Car(Product):
    year: int = models.PositiveIntegerField(
        null=True,
        validators=[MinValueValidator(1900), MaxValueValidator(datetime.now().year)],
    )
    driven_distance: int = models.PositiveIntegerField(
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(10000000)]
    )
    smoking = models.NullBooleanField()
```

새로운 테이블을 추가할때 `title`, `price`, `category`, `user` 같은 공통적으로 사용하는 필드를 가진 Product 추상모델을 상속 받아 새로운 테이블을 정의한다.



##### 장점

- 새로운 모델을 생성할때 보다 쉽게 생성이 가능하다.

##### 단점
- 채팅방이나 댓글 같은 다대다 관계가 필요한 테이블을 참조할때 외래키 적용이 복잡해진다.
- 새로운 카테고리별로 추가적인 스키마가 작성되어 관리가 힘들다.



#### 5. Concrete Base Model (**선택**)

기본적인 방법은 위 Abstract Model과 유사하지만 이 방법은 기본 클래스가 상속받은 클래스 내부의 데이터베이스 테이블로 존재해서 기본 클래스를 이용해 다대다 관계를 만들기 쉽다.

```python
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from base import models as base_models
from users import models as user_models


class Category(base_models.TimeStampedModel):
    name = models.CharField(max_length=30)


class Product(base_models.TimeStampedModel):
    title: str = models.CharField(max_length=120)
    price: int = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100000000)],
    )
    category: Category = models.ForeignKey(
        Category,
        on_delete=models.SET(lambda x: Category.objects.get(name="기타")),
        related_name="products",
    )
    user: user_models.User = models.ForeignKey(
        user_models.User, on_delete=models.CASCADE, related_name="products"
    )


class Car(Product):
    year: int = models.PositiveIntegerField(
        null=True,
        validators=[MinValueValidator(1900), MaxValueValidator(datetime.now().year)],
    )
    driven_distance: int = models.PositiveIntegerField(
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(10000000)]
    )
    smoking = models.NullBooleanField()
```



##### 장점

- 기본 클래스에서 상품의 시퀀스를 종합적으로 관리한다.
- 상품 테이블에서 공통속성으로 쿼리로 작성할 수 있다,

##### 단점
- 추상 모델과 마찬가지로 카테고리별로 새로운 스키마를 작성해야 한다.
- 단일 항목에 대해 두 개 이상의 테이블이 존재해 상품을 가져오려면 조인을 해야한다.
- 기본 클래스에서 확장 클래스에 접근할 수 없다.



#### 6. NoSQL

NoSQL을 사용한다면 Schema를 정의할 필요가 없어 수많은 카테고리를 쉽게 저장할 수 있을것같다. 하지만 Legacy 코드상 RDBMS를 사용하기 때문에 이번 과제에서는 RDBMS를 사용한다






### 3. 자동차 판매글 Seed Data 생성시 Not NULL 에러 발생(해결)

```bash
  File "/Users/dylan/.pyenv/versions/daangn-venv/lib/python3.6/site-packages/django_seed/seeder.py", line 91, in <dictcomp>
    for field, field_format in self.field_formatters.items()
  File "/Users/dylan/.pyenv/versions/daangn-venv/lib/python3.6/site-packages/django_seed/seeder.py", line 76, in format_field
    return format(inserted_entities)
  File "/Users/dylan/.pyenv/versions/daangn-venv/lib/python3.6/site-packages/django_seed/seeder.py", line 25, in func
    raise SeederException(message)
django_seed.exceptions.SeederException: Field products.Car.product_ptr cannot be null
```
Car모델에서 seed data를 생성하려고 하니 위와 같은 에러가 발생했다.
Car모델은 Product 모델을 상속받는데 스키마를 확인해 보니 아래와 같았다.

```python
migrations.CreateModel(
    name='Car',
    fields=[
        ('product_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='products.Product')),
        ('year', models.PositiveIntegerField(verbose_name='연식(년)')),
        ('driven_distance', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10000000)], verbose_name='주행 거리(km)')),
        ('smoking', models.BooleanField(default=False, verbose_name='흡연 여부')),
    ],
    options={
        'verbose_name': '차량',
        'verbose_name_plural': '차량',
    },
    bases=('products.product',),
),
```
Car모델의 product필드는 Product 모델을 상속받으며 `product_ptr`이라는 포인터로 자동으로 맵핑 되었다.

수동으로 Car 인스턴스를 생성할때에는 위와 같은 에러가 발생하지 않았지만 `django_seed` 모듈을 통해 대량의 seed data를 만들자 위 에러가 발생한 것을 보니 해당 모듈의 내부 코드에 문제가 있는것으로 판단된다.

따라서 seed data 생성 코드를 아래와 같이 Product 인스턴스를 생성한 후 Car 인스턴스에 맵핑시켜서 해당 이슈를 해결함.

```python
def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        all_users = user_models.User.objects.all()
        seeder.add_entity(
            product_models.Product,
            number,
            {
                "user": lambda x: random.choice(all_users),
                "category": product_models.Category.objects.get(name="차량"),
                "title": lambda x: seeder.faker.sentence(
                    nb_words=6, variable_nb_words=True, ext_word_list=None
                ),
                "price": lambda x: random.randint(1, 50) * 10000000,
                "describe": lambda x: "\n".join(
                    seeder.faker.texts(
                        nb_texts=10, max_nb_chars=400, ext_word_list=None
                    )
                ),
            },
        )
        products = seeder.execute()
        products = flatten(list(products.values()))
        for pk in products:
            product = product_models.Product.objects.get(pk=pk)
            product_models.Image.objects.create(
                product=product, image=f"/product_images/{random.randint(1, 31)}.jpg",
            )
            product_models.Car.objects.create(
                product_ptr=product,
                year=random.randint(1992, 2020),
                driven_distance=random.randint(1000, 300000),
                smoking=seeder.faker.boolean(),
                created=product.created,
                updated=datetime.now(),
                category=product.category,
                user=product.user,
                title=product.title,
                price=product.price,
                describe=product.describe,
            )

        self.stdout.write(self.style.SUCCESS(f"{number}개의 차량 판매글이 생성되었습니다!"))
```





### 4. 판매글 작성 유효성 검사 실패시 form 데이터 손실(미해결)

판매글을 작성하는 로직은 다음과 같다.

1. 로그인 한 사용자가 판매글 작성 후 제출
2. [`products/forms.py`](https://github.com/DylanMsK/daangn/blob/master/products/forms.py) 에서 유효성검사 진행
3. 유효성 검사를 통과하면 DB에 저장하고 하나의 필드라도 실패하면 유효성 검사에 통과한 데이터를 들고 판매글 작성페이지로 리다이렉트
4. 사용자는 유효성 검사에 실패한 필드를 다시 입력하고 제출



해당 이슈는 3번 과정에서 발생한다.

제목, 가격, 설명, 주행거리 흡연 유무 필드는 유효성 검사 후에 판매글 작성 페이지로 리다이렉트 되어도 이전 정보를 가지고 있다.

하지만 이미지와 카테고리, 연식 필드의 경우는 이전 정보를 잃어버려 필드가 초기화 되는 이슈가 발생한다.

이미지의 경우는 리다이렉트시 브라우저가 이미지를 저장하고 있지 않아서 비동기 처리를 통해 이슈를 해결해야 한다고 한다.

참고 문서는 [링크](https://medium.com/zeitcode/asynchronous-file-uploads-with-django-forms-b741720dc952) 를 참고한다.



하지만 카테고리와 연식 필드의 경우에는 [`products`](https://github.com/DylanMsK/daangn/tree/master/products) 앱의 `forms.py` 와 `views.py` , `product_list.html`에서 데이터 포맷의 미스매칭으로 발생하는 것으로 보인다. 해당 이슈를 해결하기 위해서는 django 도큐먼트와 다른 레퍼런스를 참고하여 django built-in 내부 코드를 수정해야 할 것 같다.



### 5. Heroku 배포시 이미지 경로를 못찾음(해결)

로컬에서 서버를 가동하면 이미지 경로를 정상적으로 찾지만 heroku 서버에서는 이미지 경로를 찾지 못한다.

heroku의 무료 서버를 사용하고 있기 때문에 이미지와 같이 용량이 큰 파일을 저장하지 않기 때문에 해당 이슈가 발생하는 것인데 AWS S3를 연결해 이미지를 업로드하고 조회해야 할 것 같다.





## 유닛 테스트

### 1. Users app test [[링크](https://github.com/DylanMsK/daangn/blob/master/users/tests.py)]

테스트 함수별 목적은 아래와 같다

1. 이름을 입력하고 회원가입 시도(Valid)
2. 이름을 입력하지 않고 회원가입 시도(Valid)
3. 잘못된 이메일 형식으로 회원가입 시도(Invalid)
4. 일치하지 않는 이메일 형식으로 회원가입 시도(Invalid)
5. 이미 가입된 이메일로 회원가입 시도(Invalid)
6. 익명의 유저 메인 페이지로 이동
7. 익명의 유저 로그인 페이지로 이동
8. 익명의 유저 로그인 요청
9. 익명의 유저 회원가입 페이지로 이동
10. 익명의 유저 차량 카테고리 페이지로 이동
11. 익명의 유저 로그인 정보가 필요한 페이지로 이동
12. 로그인한 유저 로그인 정보가 필요한 페이지로 이동
13. 로그인한 유저 로그인 페이지로 이동
14. 로그인한 유저 회원가입 페이지로 이동



### 2. Products app test [[링크](https://github.com/DylanMsK/daangn/blob/master/products/tests.py)]

테스트 함수별 목적은 아래와 같다

1. 판매글 등록 시도(valid)
2. 차량 카테고리로 이동
3. 차량 필터링 적용