# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-10-25 16:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_answer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='description',
            field=models.CharField(max_length=100),
        ),
    ]
