# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-20 15:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0027_product_image_compressed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='score',
            field=models.IntegerField(default=10, editable=False),
        ),
        migrations.AlterField(
            model_name='review',
            name='views',
            field=models.IntegerField(default=0, editable=False),
        ),
    ]
