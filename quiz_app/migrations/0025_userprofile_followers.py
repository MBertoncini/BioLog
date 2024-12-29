# Generated by Django 5.0.7 on 2024-09-20 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_app', '0024_remove_userprofile_followers'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='followers',
            field=models.ManyToManyField(blank=True, related_name='following', to='quiz_app.userprofile'),
        ),
    ]
