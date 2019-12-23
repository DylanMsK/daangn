from django.shortcuts import render


# Create your views here.
def error400(request, exception):
    return render(request, "404.html", status=400)


def error404(request, exception):
    return render(request, "404.html", status=404)


def error500(request):
    return render(request, "500.html", status=500)
