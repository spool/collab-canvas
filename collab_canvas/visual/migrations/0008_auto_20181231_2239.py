# Generated by Django 2.0.9 on 2018-12-31 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visual', '0007_auto_20181231_0557'),
    ]

    operations = [
        migrations.AddField(
            model_name='visualcanvas',
            name='cell_colour_range',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Maximum range of colours'),
        ),
        migrations.AddField(
            model_name='visualcell',
            name='colour_range',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Maximum range of colours'),
        ),
    ]