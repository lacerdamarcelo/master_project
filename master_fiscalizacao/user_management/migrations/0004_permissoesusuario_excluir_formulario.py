# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-11 22:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0003_auto_20160911_1615'),
    ]

    operations = [
        migrations.AddField(
            model_name='permissoesusuario',
            name='excluir_formulario',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
