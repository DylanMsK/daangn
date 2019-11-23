from django.shortcuts import render


# Create your views here.
def home_view(request):
    """
    임시적으로 메인페이지에서 보여질 view를 정의

    추후 상품 모델을 정의 하면 대체할 예정
    """
    return render(request, "home.html")
