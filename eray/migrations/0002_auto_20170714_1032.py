# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-14 17:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eray', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='view_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='answer',
            name='vote_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='question',
            name='vote_count',
            field=models.IntegerField(default=0),
        ),
    ]
