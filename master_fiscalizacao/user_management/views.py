from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout


def login(request):
    return render(request, 'user_management/login.html')


def cadastro_usuario(request):
    return render(request, 'user_management/cadastro_usuario.html')


def salvar_usuario(request):
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
                                    password=senha)
    user.save()

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
            return redirect('/formulario_vistoria/index')
        else:
            print("The password is valid, but the account has been disabled!")
    else:
        # the authentication system was unable to verify the username and password
        print("The username and password were incorrect.")


def desautenticacao(request):
    logout(request)
    return redirect('/login/')
