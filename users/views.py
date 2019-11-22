from django.views import generic
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from users import forms, models


# Create your views here.
class LoginView(generic.FormView):
    template_name = "users/login.html"
    form_class = forms.LoginForm
    success_url = reverse_lazy("base:home")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
            return redirect("base:home")
        return super().form_valid(form)


def logout_view(request):
    logout(request)
    return redirect("base:home")
