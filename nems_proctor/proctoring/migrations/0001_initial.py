# Generated by Django 4.2.10 on 2024-02-26 02:15

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exam_title', models.CharField(max_length=255, verbose_name='Exam Title')),
                ('exam_code', models.CharField(max_length=100, unique=True, verbose_name='Exam Code')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
            ],
            options={
                'verbose_name': 'Exam',
                'verbose_name_plural': 'Exams',
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proctoring.exam')),
                ('proctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='proctoring_sessions', to=settings.AUTH_USER_MODEL)),
                ('taker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_sessions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SessionRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recording_type', models.CharField(choices=[('video', 'Video'), ('audio', 'Audio'), ('screenshot', 'Screenshot')], max_length=10)),
                ('file', models.FileField(upload_to='recordings/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'ogg', 'jpg', 'png'])])),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proctoring.session')),
            ],
        ),
        migrations.CreateModel(
            name='SessionPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(upload_to='photos/')),
                ('captured_at', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proctoring.session')),
            ],
        ),
    ]
