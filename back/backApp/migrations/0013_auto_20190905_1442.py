# Generated by Django 2.2.4 on 2019-09-05 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backApp', '0008_diseno_base64_modificado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diseno',
            name='base64',
            field=models.CharField(max_length=10485750, null=True),
        ),
    ]
