# Generated by Django 2.2.1 on 2020-02-12 08:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Gmapv2', '0024_image_zoom_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='derived_from_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Gmapv2.Image'),
        ),
    ]
