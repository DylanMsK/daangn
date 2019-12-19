from django import forms
from django.template.defaultfilters import filesizeformat
from django.conf import settings
from products import models as product_models
from products.validators import ProductRegisterValidator as register_validator
from users import models as user_models


category_queryset = product_models.Category.objects.all()
CATEGORY_CHOICES = [(0, "카테고리를 선택해주세요.")] + [
    (cat.id, cat.name) for cat in category_queryset
]


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
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={"class": "form-control", "id": "productsCategory"}),
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
    smoking = forms.TypedChoiceField(
        coerce=lambda x: x == "True",
        widget=forms.RadioSelect,
        choices=((True, "예, 흡연자 입니다."), (False, "아니오, 비 흡연자 입니다."),),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(RegisterProductForm, self).__init__(*args, **kwargs)

    def clean(self):
        validator = register_validator(self.user, self.cleaned_data)
        cleaned_data, errors = validator.check()
        if errors is not None:
            for err in errors:
                self.add_error(err[0], err[1])
        else:
            self.cleaned_data = cleaned_data

    def save(self):
        category = self.cleaned_data.get("category")
        image = self.cleaned_data.pop("image")
        # 차량 카테고리의 판매글 저장
        if category.name == "차량":
            product = product_models.Car.objects.create(**self.cleaned_data)
        # 차량 이외 legacy 카테고리 만매글 저장
        elif category.name in ["인기매물", "가구/인테리어", "유아동/유아도서", "생활/가공식품", "기타"]:
            product = product_models.Product.objects.create(**self.cleaned_data)
        else:
            print("[forms.py] 잘못된 카테고리 등록 시도!!")

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
