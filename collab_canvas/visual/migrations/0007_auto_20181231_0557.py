# Generated by Django 2.0.9 on 2018-12-31 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visual', '0006_auto_20181231_0352'),
    ]

    operations = [
        migrations.AddField(
            model_name='visualcell',
            name='south_east_diagonals',
            field=models.PositiveSmallIntegerField(db_column='z_len', default=16, verbose_name='Length of south east pointed diagonal segments (DEFAULT_CELL_PARANTHETICAL)'),
        ),
        migrations.AddField(
            model_name='visualcell',
            name='south_west_diagonals',
            field=models.PositiveSmallIntegerField(db_column='t_len', default=16, verbose_name='Length of south east pointed diagonal segments (DEFAULT_CELL_PARANTHETICAL)'),
        ),
        migrations.AlterField(
            model_name='visualcanvas',
            name='cell_height',
            field=models.PositiveSmallIntegerField(default=8, verbose_name='Height of cell grid (DEFAULT_CELL_PARANTHETICAL)'),
        ),
        migrations.AlterField(
            model_name='visualcanvas',
            name='cell_width',
            field=models.PositiveSmallIntegerField(default=8, verbose_name='Width of cell grid (DEFAULT_CELL_PARANTHETICAL)'),
        ),
        migrations.AlterField(
            model_name='visualcanvas',
            name='grid_height',
            field=models.PositiveSmallIntegerField(default=8, verbose_name='Grid vertical (y) length, where max number of cells is this time grid_width (DEFAULT_GRID_PARANTHETICAL)'),
        ),
        migrations.AlterField(
            model_name='visualcanvas',
            name='grid_width',
            field=models.PositiveSmallIntegerField(default=8, verbose_name='Grid horizontal (x) length, where max number of cells is this times grid_height (DEFAULT_GRID_PARANTHETICAL)'),
        ),
        migrations.AlterField(
            model_name='visualcell',
            name='height',
            field=models.PositiveSmallIntegerField(db_column='y_len', default=8, verbose_name='Height of cell grid (DEFAULT_CELL_PARANTHETICAL)'),
        ),
        migrations.AlterField(
            model_name='visualcell',
            name='width',
            field=models.PositiveSmallIntegerField(db_column='x_len', default=8, verbose_name='Width of cell grid (DEFAULT_CELL_PARANTHETICAL)'),
        ),
    ]