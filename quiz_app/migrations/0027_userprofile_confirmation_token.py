# Generated by Django 4.2.2 on 2024-10-04 07:00

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_app', '0026_userprofile_birth_date_userprofile_institution'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='confirmation_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
