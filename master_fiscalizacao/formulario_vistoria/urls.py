from django.conf.urls import url
from . import views

app_name = 'formulario_vistoria'
urlpatterns = [
    url(r'^preenchimento_formulario_vistoria/(?P<laudo_id>[0-9]*)$', views.preenchimento_formulario_vistoria, name='preenchimento_formulario_vistoria'),
    url(r'^save_form_vistoria/(?P<laudo>[0-9]*)$', views.save_form_vistoria, name='save_form_vistoria'),
    url(r'^foto_upload/$', views.foto_upload, name='foto_upload'),
    url(r'^foto_delete/$', views.foto_delete, name='foto_delete'),
    url(r'^fill_posto_db/$', views.fill_posto_db, name='fill_posto_db'),
    url(r'^index/(?P<pagina>[0-9]*)$', views.carregar_lista_laudos, name='index'),
    url(r'^index/registration_confirm/(?P<pagina>[0-9]*)$', views.carregar_lista_laudos_confirmacao_registro, name='index_confirm'),
    url(r'^visualizar_laudo/(?P<laudo_id>[0-9]*)$', views.visualizar_laudo, name='visualizar_laudo'),
    url(r'^visualizar_editar_laudo/(?P<laudo_id>[0-9]*)$', views.visualizar_editar_laudo, name='visualizar_editar_laudo'),
    url(r'^cadastro_posto/$', views.cadastro_posto, name='cadastro_posto'),
    url(r'^solicitacao_vistoria/$', views.solicitacao_vistoria, name='solicitacao_vistoria'),
    url(r'^save_solicitacao_vistoria/$', views.save_solicitacao_vistoria, name='save_solicitacao_vistoria'),
    url(r'^assinar_laudo/(?P<laudo>[0-9]+)$', views.assinar_laudo, name='assinar_laudo'),
    url(r'^abrir_pdf/(?P<laudo>[0-9]+)$', views.abrir_pdf, name='abrir_pdf'),
]
