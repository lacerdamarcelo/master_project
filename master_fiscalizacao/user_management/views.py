from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import PermissoesUsuario, AssinaturaUsuario
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, logout, get_user_model
from django.contrib.auth import login as auth_login
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from master_fiscalizacao.settings import MEDIA_ROOT
from datetime import datetime
import os


def login(request):
    if request.user.is_authenticated():
        return redirect('/formulario_vistoria/index/1')
    else:
        return render(request, 'user_management/login.html')


def cadastro_usuario(request):
    timestamp = datetime.now()
    numero_acesso = str(timestamp.year) + str(timestamp.month) + str(timestamp.day) + str(timestamp.hour) + str(timestamp.minute) + str(timestamp.second) + str(timestamp.microsecond)
    context = {'num_acesso': numero_acesso}
    return render(request, 'user_management/cadastro_usuario.html', context)


def configurar_permissoes_usuario(request, uidb64, token):
    if uidb64 is not None and token is not None:
        uid = urlsafe_base64_decode(uidb64)
        user_model = get_user_model()
        user = user_model.objects.get(pk=uid)
        if default_token_generator.check_token(user, token) and user.is_active is False:
            context = {'user': user}
            return render(request, 'user_management/configurar_permissoes_cliente.html', context)
        else:
            if default_token_generator.check_token(user, token) is False:
                context = {'message': 'Ocorreu um erro na confirmação do registro deste usuário!'}
                return render(request, 'user_management/erro_confirmacao_registro.html', context)
            else:
                if user.is_active is True:
                    context = {'message': 'Este usuário já está ativo!'}
                    return render(request, 'user_management/erro_confirmacao_registro.html', context)
    context = {'message': 'Ocorreu um erro na confirmação do registro deste usuário!'}
    return render(request, 'user_management/erro_confirmacao_registro.html', context)


def confirmar_registro(request, user_id):
    post_data = request.POST
    visualizar_formulario_comb = post_data.get('visualizar_formulario_comb', False)
    preencher_formulario_comb = post_data.get('preencher_formulario_comb', False)
    emitir_parecer_comb = post_data.get('emitir_parecer_comb', False)
    permissao_cliente_comb = post_data.get('permissao_cliente_comb', False)
    user_model = get_user_model()
    user = user_model.objects.get(pk=user_id)
    if user is not None:
        if user.is_active is False:
            permissoes = PermissoesUsuario(visualizar_formulario=visualizar_formulario_comb,
                                           preencher_formulario=preencher_formulario_comb,
                                           emitir_parecer=emitir_parecer_comb,
                                           permissoes_clientes=permissao_cliente_comb,
                                           usuario=user
                                           )
            permissoes.save()
            user.is_active = True
            user.save()
            return render(request, 'user_management/confirmar_registro.html')
        else:
            context = {'message': 'Este usuário já está ativo!'}
            return render(request, 'user_management/erro_confirmacao_registro.html', context)
    else:
        context = {'message': 'Este usuário não existe!'}
        return render(request, 'user_management/erro_confirmacao_registro.html', context)


def send_email_registration_request(new_user, nome, sobrenome, email):
    token = default_token_generator.make_token(new_user)
    uid = urlsafe_base64_encode(force_bytes(new_user.pk))
    texto = 'Olá!\n\nVocê acaba de receber uma solicitação para registro no\n'
    texto += 'Sistema de Vistorias Master.\n'
    texto += 'Seguem abaixo as informações de cadastro fornecidas pelo\n'
    texto += 'solicitante:\n\n'
    texto += 'Nome do Usuário: ' + nome + ' ' + sobrenome + '\n'
    texto += 'Email: ' + email + '\n'
    texto += 'Para aceitar o usuário e confirmar o registro, clique na URL\n'
    texto += 'abaixo:\n\n'
    texto += 'http://' + os.environ['HOST_IP_PORT'] + '/confirmar_registro/' + str(uid)[2:-1] + '/' + str(token)
    admin_email = User.objects.get(is_superuser=True).email
    send_mail(
        '[Sistema de Vistoria Master] Solicitação de Cadastro',
        texto,
        'noreply@mastergestaoambiental.com',
        [admin_email],
        fail_silently=False,
    )


@csrf_exempt
def assinatura_upload(request, numero_acesso):
    directory = MEDIA_ROOT + '/assinaturas'
    os.makedirs(directory, exist_ok=True)
    filename = numero_acesso + '_assinatura' + '.' + request.FILES['input-assinatura'].name.split('.')[1]
    with open(directory + '/' + filename, 'wb+') as destination:
        for chunk in request.FILES['input-assinatura'].chunks():
            destination.write(chunk)

    assinatura = AssinaturaUsuario(endereco=directory + '/' + filename,
                                   usuario=None)
    assinatura.save()
    return render(request, 'user_management/empty_json.json')


def salvar_usuario(request, numero_acesso):
    post_data = request.POST

    nome = post_data['nome']
    sobrenome = post_data['sobrenome']
    email = post_data['email']
    user = post_data['user']
    senha = post_data['senha']

    user = User.objects.create_user(first_name=nome,
                                    last_name=sobrenome,
                                    email=email,
                                    username=user,
                                    password=senha,
                                    is_active=False)
    user.save()
    directory = MEDIA_ROOT + '/assinaturas'
    files = os.listdir(directory)
    filename = ''
    for file in files:
        if numero_acesso + '_assinatura' in file:
            filename = file
    assinatura = AssinaturaUsuario.objects.get(endereco=directory + '/' + filename)
    assinatura.usuario = user
    assinatura.save()
    send_email_registration_request(user, nome, sobrenome, email)
    return render(request, 'user_management/login.html')


def autenticacao(request):
    post_data = request.POST
    senha = post_data['senha']
    usuario = post_data['usuario']
    user = authenticate(username=usuario, password=senha)
    if user is not None:
        # the password verified for the user
        if user.is_active:
            auth_login(request, user)
            return redirect('/formulario_vistoria/index/1')
        else:
            print("The password is valid, but the account has been disabled!")
    else:
        # the authentication system was unable to verify the username and password
        print("The username and password were incorrect.")


def desautenticacao(request):
    logout(request)
    return redirect('/login/')
