# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-10-06 14:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_auto_20171005_1007'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertotp',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
