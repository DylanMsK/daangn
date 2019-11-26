from django.test import TestCase
from django.urls import reverse, resolve
from users import models, forms


# Create your tests here.
class UserFormTest(TestCase):
    """
    사용자의 로그인과 회원가입시 사용하는 form의 유효성 검사 테스트
    """

    email = "test_user@gmail.com"
    password = "secret"

    def setUp(self):
        self.test_user = models.User.objects.create_user(
            username="already_taken@gmail.com",
            password="secret",
            email="already_taken@gmail.com",
        )

    # 이름을 등록하고 회원가입 시도(Valid)
    def test_signup_form_with_name_valid(self):
        form = forms.SignUpForm(
            data={
                "email": self.email,
                "password": self.password,
                "confirm_password": self.password,
                "name": "테스트 유저",
            }
        )
        self.assertTrue(form.is_valid())

    # 이름을 등록하지 않고 회원가입 시도(Valid)
    def test_signup_form_without_name_valid(self):
        form = forms.SignUpForm(
            data={
                "email": self.email,
                "password": self.password,
                "confirm_password": self.password,
            }
        )
        self.assertTrue(form.is_valid())

    # 잘못된 이메일 형식으로 회원가입 시도(Invalid)
    def test_signup_form_invalid_email(self):
        form = forms.SignUpForm(
            data={
                "email": "test@@",
                "password": self.password,
                "confirm_password": self.password,
            }
        )
        self.assertFalse(form.is_valid())

    # 일치하지 않는 이메일 형식으로 회원가입 시도(Invalid)
    def test_signup_form_invalid_confirm_password(self):
        form = forms.SignUpForm(
            data={
                "email": self.email,
                "password": self.password,
                "confirm_password": self.password + "!",
            }
        )
        self.assertFalse(form.is_valid())

    # 이미 가입된 이메일로 회원가입 시도(Invalid)
    def test_signup_form_already_used_email_invalid(self):
        form = forms.SignUpForm(
            data={
                "email": self.test_user.username,
                "password": self.password,
                "confirm_password": self.password,
            }
        )
        self.assertFalse(form.is_valid())


class UserViewTest(TestCase):
    """
    유저가 로그인이 필요한 페이지 까지 이동 과정 테스트
    """

    email = "test_user@gmail.com"
    password = "secret"

    def setUp(self):
        self.test_user = models.User.objects.create_user(
            username=self.email, password=self.password, email=self.email
        )

    # 익명의 유저 메인 페이지로 이동
    def test_anonymous_home_view(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    # 익명의 유저 로그인 페이지로 이동
    def test_anoymous_login_get_view(self):
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")

    # 익명의 유저 로그인 요청
    def test_anoymous_login_post_view(self):
        response = self.client.post(
            reverse("users:login"), {"email": self.email, "password": self.password},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("products:home"))

    # 익명의 유저 회원가입 페이지로 이동
    def test_anonympus_signup_get_view(self):
        response = self.client.get(reverse("users:signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/signup.html")

    # 익명의 유저 차량 카테고리 페이지로 이동
    def test_anonymous_car_list_view(self):
        response = self.client.get(reverse("products:car_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/product_list.html")

    # 익명의 유저 로그인 정보가 필요한 페이지로 이동
    def test_anonymous_product_create_view(self):
        response = self.client.get(reverse("products:register"))
        self.assertEqual(response.status_code, 302)

    # 로그인한 유저 로그인 정보가 필요한 페이지로 이동
    def test_user_product_create_view(self):
        user = self.client.login(username=self.email, password=self.password)
        self.assertTrue(user)
        response = self.client.get(reverse("products:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/product_create.html")

    # 로그인한 유저 로그인 페이지로 이동
    def test_user_login_view(self):
        user = self.client.login(username=self.email, password=self.password)
        self.assertTrue(user)
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, 302)

    # 로그인한 유저 회원가입 페이지로 이동
    def test_user_signup_view(self):
        user = self.client.login(username=self.email, password=self.password)
        self.assertTrue(user)
        response = self.client.get(reverse("users:signup"))
        self.assertEqual(response.status_code, 302)
