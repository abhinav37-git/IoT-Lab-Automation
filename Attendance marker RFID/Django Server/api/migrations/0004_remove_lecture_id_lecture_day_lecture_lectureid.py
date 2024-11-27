# Generated by Django 4.2.1 on 2023-05-15 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_lecture_room_scannerroom_student_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lecture',
            name='id',
        ),
        migrations.AddField(
            model_name='lecture',
            name='day',
            field=models.CharField(default='', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lecture',
            name='lectureID',
            field=models.CharField(default='', max_length=15, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]