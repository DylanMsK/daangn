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
