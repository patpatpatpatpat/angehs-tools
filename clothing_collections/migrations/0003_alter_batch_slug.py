# Generated by Django 3.2.3 on 2021-05-17 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clothing_collections', '0002_auto_20210517_1123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch',
            name='slug',
            field=models.SlugField(blank=True),
        ),
    ]