# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-18 18:21
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('relationaldb', '0004_auto_20171206_1753'),
    ]

    operations = [
        migrations.CreateModel(
            name='TournamentParticipantBalance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=0, default=0, max_digits=80)),
            ],
        ),
        migrations.RemoveField(
            model_name='tournamentparticipant',
            name='balance',
        ),
        migrations.AddField(
            model_name='tournamentparticipantbalance',
            name='participant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relationaldb.TournamentParticipant'),
        ),
    ]
