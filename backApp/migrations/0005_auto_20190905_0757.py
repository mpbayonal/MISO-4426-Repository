# Generated by Django 2.2.4 on 2019-09-05 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backApp', '0004_diseno_apellido'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diseno',
            name='estado',
            field=models.CharField(max_length=500),
        ),
    ]
