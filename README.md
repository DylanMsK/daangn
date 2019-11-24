# 당근마켓 웹 개발 과제

## 이슈

### 1. 사용자가 회원가입시 이름 필드 부재

스켈레톤상의 DB 스키마를 보면 name을 입력받게 되어있지만 `signup.html` 상에는 이름을 입력받는 `input tag` 가 없음.
따라서 users 모델의 name 필드에 null 값은 허용하지 않지만 빈 스트링을 등록 가능하게 변경하고, 회원가입시 이름 입력은 선택사항으로 변경

### 2. Product Model 확장

기존의 상품들은 제목, 카테고리, 가격, 이미지, 상품 등록자 필드로 충분했지만 차량의 카테고리에는 연식, 주행거리, 흡연 여부 등이 추가된다.

또한, 향후 추가될 부동산, 도서 등의 다양한 카테고리가 추가될 것을 고려하여 DB를 설계해야 한다.

#### 1. Naive Model

가장 간단한 중고 마켓 DB 모델링은 다음과 같다.
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
```

이미 등록된 카테고리 상품에는 공통적인 속성만 필요하므로 위 schema로 모든 상품을 등록할 수 있다.

##### 장점
- 코드의 이해가 쉽고 유지보수가 쉽다.

##### 단점
- 상품 속성에 대한 다향성이 제한된다.

<br>

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

<br>

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
- 빈 값의 필드가 레코드별로 퍼져있는 것을 방지할 수 있다.
- 새로운 속성을 추가하기 쉽다.

##### 단점
- JSONField를 제공하는 데이터베이스에서만 사용 가능하다.
- 유효성검사가 복잡해진다.
- JSONField 내부에는 Schema를 정의할 수 없다.

<br>

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
- 채팅방이나 댓글 같은 다대다 관계가 필요한 테이블을 참조할때 외래키 적용이 복잡하다.
- 새로운 카테고리별로 추가적인 스키마가 작성되어 관리가 힘들다.

<br>

#### 5. Concrete Base Model

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

<br>

#### 6. NoSQL

NoSQL을 사용한다면 Schema를 정의할 필요가 없어 수많은 카테고리를 쉽게 저장할 수 있을것같다. 하지만 Legacy 코드상 MySQL이 사용되어 NoSQL이 아닌 RDBMS를 사용한다.