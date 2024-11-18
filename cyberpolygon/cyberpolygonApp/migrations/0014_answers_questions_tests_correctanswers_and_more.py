# Generated by Django 5.1 on 2024-10-16 12:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cyberpolygonApp', '0013_alter_post_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answers',
            fields=[
                ('id', models.AutoField(db_index=True, primary_key=True, serialize=False)),
                ('answer_test', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Questions',
            fields=[
                ('id', models.AutoField(db_index=True, primary_key=True, serialize=False)),
                ('question_test', models.TextField()),
                ('created_at', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Tests',
            fields=[
                ('id', models.AutoField(db_index=True, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(max_length=255)),
                ('created_at', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='CorrectAnswers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cyberpolygonApp.answers')),
                ('question_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cyberpolygonApp.questions')),
            ],
        ),
        migrations.AddField(
            model_name='answers',
            name='question_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cyberpolygonApp.questions'),
        ),
        migrations.AddField(
            model_name='questions',
            name='test_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cyberpolygonApp.tests'),
        ),
    ]