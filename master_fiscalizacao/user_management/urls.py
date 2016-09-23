from django.conf.urls import url
from . import views

app_name = 'user_management'

urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^cadastro_usuario/$', views.cadastro_usuario, name='cadastro_usuario'),
    url(r'^salvar_usuario/(?P<numero_acesso>[0-9]+)$', views.salvar_usuario, name='salvar_usuario'),
    url(r'^autenticacao/$', views.autenticacao, name='autenticacao'),
    url(r'^desautenticacao/$', views.desautenticacao, name='desautenticacao'),
    url(r'^confirmar_registro/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.configurar_permissoes_usuario, name='configurar_permissoes_usuario'),
    url(r'^confirmar_registro/(?P<user_id>[0-9]+)/$', views.confirmar_registro, name='confirmar_registro'),
    url(r'^assinatura_upload/(?P<numero_acesso>[0-9]+)$', views.assinatura_upload, name='assinatura_upload'),
]
