# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-05 20:07
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0017_auto_20170805_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='cons',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=20), null=True, size=10),
        ),
        migrations.AlterField(
            model_name='review',
            name='pros',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=20), null=True, size=10),
        ),
    ]
