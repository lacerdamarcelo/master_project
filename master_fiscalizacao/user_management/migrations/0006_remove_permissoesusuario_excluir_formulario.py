# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-18 03:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0005_remove_permissoesusuario_receber_alerta_pedidos_vistoria'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='permissoesusuario',
            name='excluir_formulario',
        ),
    ]
