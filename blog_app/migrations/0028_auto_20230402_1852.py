# Generated by Django 3.2.9 on 2023-04-02 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0027_alter_usermodels_biographie'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usermodels',
            name='biographie',
        ),
        migrations.AddField(
            model_name='usermodels',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]