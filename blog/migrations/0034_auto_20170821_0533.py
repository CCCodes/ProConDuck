# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-21 09:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0033_auto_20170820_2201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='slug',
            field=models.SlugField(editable=False, max_length=255, unique=True),
        ),
    ]
