# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-27 10:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0049_auto_20170825_2149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='score',
            field=models.FloatField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='review',
            name='score',
            field=models.FloatField(default=5),
        ),
    ]
