# Generated by Django 5.0.7 on 2024-08-02 16:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_app', '0021_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizquestion',
            name='user_answer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quiz_question_user_answers', to='quiz_app.species'),
        ),
    ]
