# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-08-06 21:28
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formulario_vistoria', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='laudo',
            name='data_criacao',
            field=models.DateField(default=datetime.datetime(2016, 8, 6, 18, 28, 17, 198670)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='laudo',
            name='data_permissao',
            field=models.DateField(null=True),
        ),
    ]
