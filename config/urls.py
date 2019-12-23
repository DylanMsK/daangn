from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls import handler400, handler404, handler500
from django.conf.urls.static import static


handler400 = "base.views.error400"
handler404 = "base.views.error404"
handler500 = "base.views.error500"

urlpatterns = [
    path("", include("products.urls", namespace="products")),
    path("users/", include("users.urls", namespace="users")),
    path("admin/", admin.site.urls),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
