from django import forms
from products import models


class RegisterProductForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(RegisterProductForm, self).__init__(*args, **kwargs)

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
        queryset=models.Category.objects.all(),
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
                "step": 1000,
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
            choices=[(0, "차량 연식을 선택해주세요.")] + [(x, x) for x in range(2020, 1990, -1)],
            attrs={"class": "form-control", "id": "carModelYear"},
        ),
    )
    driven_distance = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "carMileage",
                "placeholder": "주행거리를 입력해주세요.(km)",
            }
        ),
    )
    smoking = forms.BooleanField(
        widget=forms.RadioSelect(
            choices=((True, "예, 흡연자 입니다."), (False, "아니오, 비 흡연자 입니다."),)
        )
    )

    def save(self):
        image = self.cleaned_data.get("image")
        title = self.cleaned_data.get("title")
        categories = self.cleaned_data.get("categories")
        price = self.cleaned_data.get("price")
        describe = self.cleaned_data.get("describe")
        year = self.cleaned_data.get("year")
        driven_distance = self.cleaned_data.get("driven_distance")
        smoking = self.cleaned_data.get("smoking")
        car = models.Car.objects.create(
            user=self.user,
            category=categories,
            title=title,
            price=price,
            describe=describe,
            year=year,
            driven_distance=driven_distance,
            smoking=smoking,
        )
        models.Image.objects.create(image=image, product=car)
        return car
