# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-24 10:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0043_auto_20170824_0552'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promotion',
            name='company',
        ),
        migrations.AddField(
            model_name='promotion',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='blog.Product'),
        ),
    ]
