from django import forms
from users import models


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "id": "inputEmail", "placeholder": "이메일 입력"}
        ),
        label="이메일",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "inputPassword",
                "placeholder": "비밀번호 입력",
            }
        ),
        label="비밀번호",
    )

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        try:
            user = models.User.objects.get(username=email)
            if user.check_password(password):
                return self.cleaned_data
            else:
                self.add_error("password", "비밀번호를 확인해 주세요")
        except models.User.DoesNotExist:
            self.add_error("email", "등록된 회원이 아닙니다")


class SignUpForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "id": "inputName", "placeholder": "이름 입력"}
        ),
        label="이름(선택)",
        required=True,
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "id": "inputEmail", "placeholder": "이메일 입력"}
        ),
        label="이메일",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "inputPassword",
                "placeholder": "비밀번호 입력",
            }
        ),
        label="비밀번호",
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "confirmPassword",
                "placeholder": "비밀번호 확인하기",
            }
        ),
        label="비밀번호 확인",
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        try:
            user = models.User.objects.get(username=email)
            raise forms.ValidationError("해당 이메일은 이미 등록되어 있습니다")
        except models.User.DoesNotExist:
            return email

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password == confirm_password:
            return password
        else:
            raise forms.ValidationError("비밀번호가 일치하지 않습니다")

    def save(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        name = self.cleaned_data.get("name")
        models.User.objects.create_user(
            username=email, email=email, password=password, name=name
        )
