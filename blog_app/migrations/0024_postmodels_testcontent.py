# Generated by Django 3.2.9 on 2023-03-13 12:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0023_postmodels_bookmark'),
    ]

    operations = [
        migrations.AddField(
            model_name='postmodels',
            name='testcontent',
            field=models.FileField(default=django.utils.timezone.now, upload_to='posts_image/'),
            preserve_default=False,
        ),
    ]
