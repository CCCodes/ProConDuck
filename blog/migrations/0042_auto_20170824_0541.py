# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-24 09:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0041_auto_20170823_1149'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='links',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='image_thumb_url',
            field=models.URLField(blank=True, editable=False),
        ),
    ]
