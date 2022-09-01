# Generated by Django 3.2.6 on 2022-09-01 10:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(default='Базовое описание (базированное)', max_length=2000)),
                ('header', models.CharField(max_length=200)),
                ('date', models.DateField(default='2021-01-01')),
                ('time', models.TimeField(default='00:00:00')),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('image', models.ImageField(blank=True, null=True, upload_to='media/', verbose_name='Картинка')),
                ('description', models.CharField(default='Базовое описание (базированное)', max_length=2000, verbose_name='Название')),
            ],
            options={
                'db_table': 'courses',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='CourseSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'subs',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Homework',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(blank=True, max_length=5000, null=True, verbose_name='Описание')),
                ('status', models.CharField(choices=[('Complete', 'Complete'), ('In_progress', 'In Progress'), ('Failed', 'Failed')], default='In_progress', max_length=20)),
            ],
            options={
                'db_table': 'homework',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='HomeworkFiles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='media/', verbose_name='Файл')),
            ],
            options={
                'db_table': 'homework_files',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(null=True, upload_to='media/', verbose_name='Картинка')),
                ('video', models.FileField(blank=True, null=True, upload_to='media/', verbose_name='Видео')),
                ('in_module_id', models.IntegerField()),
                ('name', models.CharField(max_length=1000, verbose_name='Название')),
                ('text', models.CharField(max_length=5000, verbose_name='Описание')),
                ('question', models.CharField(max_length=1000, verbose_name='Задание')),
            ],
            options={
                'db_table': 'lessons',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='LessonFiles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='media/', verbose_name='Файл')),
            ],
            options={
                'db_table': 'lessons_files',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='История Кочки', max_length=100, verbose_name='Название')),
                ('in_course_id', models.IntegerField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='media/', verbose_name='Картинка')),
                ('description', models.CharField(default='Базовое описание (базированное)', max_length=2000, verbose_name='Название')),
            ],
            options={
                'db_table': 'modules',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Special',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header', models.CharField(max_length=100, verbose_name='Название')),
                ('image', models.ImageField(null=True, upload_to='media/', verbose_name='Картинка')),
                ('description', models.CharField(default='Базовое описание (базированное)', max_length=2000, verbose_name='Название')),
            ],
            options={
                'db_table': 'special',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Timer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.TimeField()),
                ('text', models.CharField(max_length=1000, verbose_name='Описание')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.lesson')),
            ],
            options={
                'db_table': 'timers',
                'managed': True,
            },
        ),
    ]
