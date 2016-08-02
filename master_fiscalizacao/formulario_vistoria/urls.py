from django.conf.urls import url
from . import views

app_name = 'formulario_vistoria'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^preenchimento_formulario_vistoria/$', views.preenchimento_formulario_vistoria, name='preenchimento_vistoria_form'),
    url(r'^save_form_vistoria/$', views.save_form_vistoria, name='save_form_vistoria'),
    url(r'^foto_upload/$', views.foto_upload, name='foto_upload'),
    url(r'^foto_delete/$', views.foto_delete, name='foto_delete'),
]
