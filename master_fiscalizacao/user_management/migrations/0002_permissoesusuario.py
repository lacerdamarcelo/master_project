# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-11 19:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_management', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PermissoesUsuario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visualizar_formulario', models.BooleanField()),
                ('preencher_formulario', models.BooleanField()),
                ('receber_alerta_pedidos_vistoria', models.BooleanField()),
                ('emitir_parecer', models.BooleanField()),
                ('permissoes_clientes', models.BooleanField()),
                ('usuario', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
