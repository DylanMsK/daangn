from django import forms
from users import models


class LoginForm(forms.Form):
    email = forms.EmailField(label="이메일")
    password = forms.CharField(widget=forms.PasswordInput, label="비밀번호")

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
