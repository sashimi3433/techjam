# Generated by Django 5.1.3 on 2025-02-02 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_timelineactivity'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='experience_points',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='customuser',
            name='tasks_completed',
            field=models.IntegerField(default=0),
        ),
    ]
