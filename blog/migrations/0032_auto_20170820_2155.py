# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-21 01:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0031_auto_20170820_2033'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='keywords',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='review',
            name='slug',
            field=models.SlugField(blank=True),
        ),
    ]
