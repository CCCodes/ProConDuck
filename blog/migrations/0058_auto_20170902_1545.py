# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-02 19:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0057_auto_20170902_1542'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='score',
            field=models.FloatField(default=0, editable=False),
        ),
    ]
