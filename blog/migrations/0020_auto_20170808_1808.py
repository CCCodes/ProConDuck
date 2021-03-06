# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-08 22:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0019_auto_20170807_0607'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='number',
            field=models.IntegerField(unique=True),
        ),
    ]
