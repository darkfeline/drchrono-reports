# -*- coding: utf-8 -*-

# Copyright (C) 2016  Allen Li
#
# This file is part of drchrono-reports.
#
# drchrono-reports is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# drchrono-reports is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with drchrono-reports.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=256)),
                ('last_name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256)),
                ('archived', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='ReportsUser',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('access_token', models.CharField(max_length=256)),
                ('refresh_token', models.CharField(max_length=256)),
                ('expires', models.DateTimeField(null=True)),
                ('last_updated', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256)),
                ('archived', models.BooleanField()),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.Doctor')),
            ],
        ),
        migrations.CreateModel(
            name='UserDoctor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.Doctor')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.ReportsUser')),
            ],
        ),
        migrations.CreateModel(
            name='UserTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.Template')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.ReportsUser')),
            ],
        ),
        migrations.CreateModel(
            name='Value',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.Appointment')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.Field')),
            ],
        ),
        migrations.AddField(
            model_name='field',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.Template'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.Doctor'),
        ),
        migrations.AlterUniqueTogether(
            name='usertemplate',
            unique_together=set([('user', 'template')]),
        ),
        migrations.AlterUniqueTogether(
            name='userdoctor',
            unique_together=set([('user', 'doctor')]),
        ),
    ]
