# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-21 02:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0032_auto_20170820_2155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='slug',
            field=models.SlugField(blank=True, max_length=255),
        ),
    ]
