from django.conf.urls import url
from . import views

app_name = 'user_management'

urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^cadastro_usuario/$', views.cadastro_usuario, name='cadastro_usuario'),
    url(r'^salvar_usuario/$', views.salvar_usuario, name='salvar_usuario'),
    url(r'^autenticacao/$', views.autenticacao, name='autenticacao'),
    url(r'^desautenticacao/$', views.desautenticacao, name='desautenticacao'),
]
