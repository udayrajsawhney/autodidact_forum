# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-10-28 19:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0029_auto_20181029_0102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(related_name='post_tag', to='app.Tag'),
        ),
    ]
