# Generated by Django 2.2.4 on 2019-09-04 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backApp', '0003_usercustom_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='diseno',
            name='apellido',
            field=models.CharField(default='martinez', max_length=500),
            preserve_default=False,
        ),
    ]
