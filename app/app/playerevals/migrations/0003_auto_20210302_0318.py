# Generated by Django 3.1 on 2021-03-02 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playerevals', '0002_auto_20210227_2023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='data',
            field=models.TextField(),
        ),
    ]
