# Generated by Django 2.2.1 on 2019-09-02 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Gmapv2', '0010_auto_20190903_0321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jsmappedworks',
            name='is_marked',
            field=models.BooleanField(null=True),
        ),
    ]
