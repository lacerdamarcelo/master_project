from django.conf.urls import include, url

from django.contrib import admin

urlpatterns = [
    url(r"^admin/", include(admin.site.urls)),
    url(r"^formulario_vistoria/", include('formulario_vistoria.urls')),
    url(r"^", include('user_management.urls')),
]
