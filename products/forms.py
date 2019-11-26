from django import forms
from django.template.defaultfilters import filesizeformat
from django.conf import settings
from products import models as product_models
from users import models as user_models


class RegisterProductForm(forms.Form):
    image = forms.FileField(
        widget=forms.FileInput(
            attrs={
                "class": "upload-name",
                "id": "ex_filename",
                "placeholder": "파일선택",
                "name": "image",
            }
        )
    )
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "productsTitle",
                "placeholder": "제품 이름을 입력해주세요.",
            }
        ),
        max_length=120,
    )
    categories = forms.ModelChoiceField(
        queryset=product_models.Category.objects.all(),
        widget=forms.Select(attrs={"class": "form-control", "id": "productsCategory"}),
        empty_label="카테고리를 선택해주세요.",
    )
    price = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "productsPrice",
                "placeholder": "가격을 입력해주세요. (￦)",
                "min": 0,
            }
        ),
    )
    describe = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "id": "productsDescription",
                "placeholder": "제품 설명을 작성해주세요.",
                "rows": "10",
            }
        ),
    )
    year = forms.IntegerField(
        widget=forms.Select(
            choices=[(0, "차량 연식을 선택해주세요.")] + [(x, x) for x in range(2020, 1989, -1)],
            attrs={"class": "form-control", "id": "carModelYear"},
        ),
        required=False,
    )
    driven_distance = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "carMileage",
                "placeholder": "주행거리를 입력해주세요.(km)",
            }
        ),
        required=False,
    )
    smoking = forms.BooleanField(
        widget=forms.RadioSelect(
            choices=((True, "예, 흡연자 입니다."), (False, "아니오, 비 흡연자 입니다."),)
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(RegisterProductForm, self).__init__(*args, **kwargs)

    def clean(self):
        image = self.cleaned_data.get("image")
        title = self.cleaned_data.get("title")
        categories = self.cleaned_data.get("categories")
        price = self.cleaned_data.get("price")
        describe = self.cleaned_data.get("describe")
        year = self.cleaned_data.get("year")
        driven_distance = self.cleaned_data.get("driven_distance")
        smoking = self.cleaned_data.get("smoking")

        # 로그인된 사용자 체크
        if not user_models.User.objects.filter(id=self.user.id).exists():
            self.add_error(None, "로그인된 사용자만 판매글을 작성할 수 있습니다.")

        # 이미지 업로드 체크
        content_type = image.content_type.split("/")[0]
        if content_type in settings.CONTENT_TYPES:
            if image.size > settings.MAX_UPLOAD_SIZE:
                self.add_error(
                    "image",
                    "10MB 이하의 이미지만 업로드할 수 있습니다. 현재 파일 용량: %s"
                    % filesizeformat(image.size),
                )
        else:
            self.add_error("image", "이미지 파일만 첨부할 수 있습니다.")

        # 제목 입력 체크
        if title is None:
            self.add_error("title", "제품 이름을 입력해주세요.")

        # 카테고리 선택 체크
        try:
            category = product_models.Category.objects.get(name=categories)
            # 차량 카테고리 선택시 추가 필트 체크
            if category.name == "차량":
                if year is None:
                    self.add_error("year", "차량 연식을 선택해주세요.")
                else:
                    if year < 1990 or year > 2020:
                        self.add_error("year", "1990년에서 2020년 사이에 제작된 차량만 등록 가능합니다.")

                if driven_distance is None:
                    self.add_error("driven_distance", "주행거리를 입력해주세요.(km)")
                else:
                    if driven_distance < 0 or driven_distance > 100000:
                        self.add_error(
                            "driven_distance", "주행거리가 0km에서 100,000km 까지의 차량만 등록 가능합니다."
                        )
                if smoking is None:
                    self.add_error("smoking", "흡연유무를 선택해 주세여.")
        except product_models.Category.DoesNotExist:
            self.add_error("categories", "카테고리를 선택해주세요.")

        # 가격 입력 체크
        if price is None:
            self.add_error("price", "가격을 입력해주세요. (￦)")
        else:
            if price < 0 or price > 100000000:
                self.add_error("price", "1억원 이하의 금액만 등록 가능합니다.")

        # 설명 입력 체크
        if describe is None:
            self.add_error("describe", "제품 설명을 작성해주세요.")

    def save(self):
        image = self.cleaned_data.get("image")
        title = self.cleaned_data.get("title")
        categories = self.cleaned_data.get("categories")
        price = self.cleaned_data.get("price")
        describe = self.cleaned_data.get("describe")

        # 차량 카테고리의 판매글 저장
        if categories.name == "차량":
            year = self.cleaned_data.get("year")
            driven_distance = self.cleaned_data.get("driven_distance")
            smoking = self.cleaned_data.get("smoking")
            product = product_models.Car.objects.create(
                user=self.user,
                category=categories,
                title=title,
                price=price,
                describe=describe,
                year=year,
                driven_distance=driven_distance,
                smoking=smoking,
            )
        else:
            product = product_models.Product.objects.create(
                user=self.user,
                category=categories,
                title=title,
                price=price,
                describe=describe,
            )
        product_models.Image.objects.create(image=image, product=product)
        return product


class FilterForm(forms.Form):
    year = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "input-slider-item",
                "id": "sliderCarModelYear",
                "aria-describedby": "sliderCarModelYearHelp",
            }
        )
    )
    driven_distance = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "input-slider-item",
                "id": "sliderCarMileage",
                "aria-describedby": "sliderCarMileageHelp",
            }
        )
    )
    smoking = forms.NullBooleanField(
        widget=forms.RadioSelect(
            choices=(("total", "전체"), ("true", "흡연"), ("false", "비흡연"),)
        ),
        initial="total",
        required=False,
    )

    def clean_year(self):
        year = self.cleaned_data.get("year")
        min_year, max_year = year.split(",")
        self.cleaned_data["min_year"] = int(min_year)
        self.cleaned_data["max_year"] = int(max_year)
        return year

    def clean_driven_distance(self):
        driven_distance = self.cleaned_data.get("driven_distance")
        min_driven_distance, max_driven_distance = driven_distance.split(",")
        self.cleaned_data["min_driven_distance"] = int(min_driven_distance)
        self.cleaned_data["max_driven_distance"] = int(max_driven_distance)
        return driven_distance

    def clean_smoking(self):
        smoking = self.cleaned_data.get("smoking", None)
        if smoking is not None:
            if smoking == "true":
                return True
            return False
