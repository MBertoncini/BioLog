# Generated by Django 5.0.7 on 2024-09-22 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_app', '0025_userprofile_followers'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='birth_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='institution',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
