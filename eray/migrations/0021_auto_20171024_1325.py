# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-10-24 20:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eray', '0020_tag_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='tags',
            field=models.ManyToManyField(related_name='questions', to='eray.Tag'),
        ),
    ]