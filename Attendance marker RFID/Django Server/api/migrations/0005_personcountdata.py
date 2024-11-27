# Generated by Django 5.0.3 on 2024-03-16 14:21

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_remove_lecture_id_lecture_day_lecture_lectureid'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonCountData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('date', models.DateField(default=django.utils.timezone.localdate)),
                ('time', models.TimeField(default=django.utils.timezone.localtime)),
            ],
        ),
    ]