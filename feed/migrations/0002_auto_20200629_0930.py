# Generated by Django 3.0.7 on 2020-06-29 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_bookmarked',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='is_liked',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]
