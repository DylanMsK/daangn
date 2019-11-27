from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse, resolve
from products import models, forms
from users import models as user_models


# Create your tests here.
class ProductFormTest(TestCase):
    """
    판매글 등록시 사용하는 form의 유효성 검사 테스트
    """

    email = "test_user@gmail.com"
    password = "secret"
    sample_image = (
        b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
        b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
        b"\x02\x4c\x01\x00\x3b"
    )
    image = (
        SimpleUploadedFile("sample_image", sample_image, content_type="image/gif"),
    )
    title = "자동차 판매 테스트입니다."
    category = models.Category.objects.get(name="차량")
    price = 10000000
    describe = "test"
    year = 2019
    driven_distance = 4500
    smoking = False
    valid_data = {
        "image": image,
        "title": title,
        "category": category.id,
        "price": price,
        "describe": describe,
        "year": year,
        "driven_distance": driven_distance,
        "smoking": smoking,
    }

    # 판매글을 등록할 유저 생성
    def setUp(self):
        self.test_user = user_models.User.objects.create_user(
            username=self.email, password=self.password, email=self.email,
        )
        user = self.client.login(username=self.email, password=self.password)
        self.assertTrue(user)
        response = self.client.get(reverse("products:register"))
        self.assertEqual(response.status_code, 200)

    # 1. 판매글 등록 시도(valid)
    @override_settings(MEDIA_ROOT="test/")
    def test_register_valid(self):
        form = self.client.post(reverse("products:register"), self.valid_data)
        self.assertTrue(form.is_valid())


class ProductViewTest(TestCase):
    """
    유저가 상품 리스트를 조회하고 필터링하는 과정 테스트
    """

    # 2. 차량 카테고리로 이동
    def test_products_view(self):
        response = self.client.get(reverse("products:car_list"))
        self.assertEqual(response.status_code, 200)

    # 3. 차량 필터링 적용
    def test_products_filter_view(self):
        response = self.client.get(
            "/car/?year=2010,2020&driven_distance=0,100000&smoking=True"
        )
        self.assertEqual(response.status_code, 200)
