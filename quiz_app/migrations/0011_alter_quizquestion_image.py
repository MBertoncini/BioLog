# Generated by Django 5.0.7 on 2024-07-29 08:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_app', '0010_alter_quizquestion_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizquestion',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='quiz_app.image'),
        ),
    ]
