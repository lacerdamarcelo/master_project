from django.db import models
from django.contrib.auth.models import User


class AssinaturaUsuario(models.Model):
    endereco = models.CharField(max_length=500)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)

    def __str__(self):
        if self.usuario is not None:
            return 'Assinatura de ' + self.usuario.first_name + ' ' + self.usuario.last_name
        else:
            return 'Assinatura de ???'


class PermissoesUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    visualizar_formulario = models.BooleanField()
    preencher_formulario = models.BooleanField()
    emitir_parecer = models.BooleanField()
    permissoes_clientes = models.BooleanField()

    def __str__(self):
        return self.usuario.first_name + ' ' + self.usuario.last_name
