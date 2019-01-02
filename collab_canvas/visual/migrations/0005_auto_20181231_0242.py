# Generated by Django 2.0.9 on 2018-12-31 02:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('visual', '0004_auto_20181229_0319'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='visualcelledit',
            options={'get_latest_by': 'timestamp'},
        ),
        migrations.AddField(
            model_name='visualcanvas',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Date Created'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='visualcell',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Date cell was created'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='visualcell',
            name='neighbours_may_edit',
            field=models.BooleanField(default=True, verbose_name="Whether artist's neighbours are allowed to edit this cell"),
        ),
        migrations.AddField(
            model_name='visualcelledit',
            name='artist',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='visualcelledit',
            name='neighbour_edit',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(0, 'North'), (1, 'East'), (2, 'South'), (3, 'West')], null=True, verbose_name='Which neighbour, if any, is the source of the edit'),
        ),
        migrations.AlterField(
            model_name='visualcell',
            name='artist',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='visual_cells', to=settings.AUTH_USER_MODEL, verbose_name='Artist assigned this part of the Canvas'),
        ),
        migrations.AlterField(
            model_name='visualcell',
            name='canvas',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visual_cells', to='visual.VisualCanvas', verbose_name='Which canvas this cell is in'),
        ),
        migrations.AlterField(
            model_name='visualcell',
            name='is_editable',
            field=models.BooleanField(default=True, verbose_name='Whether artists are allowed to edit this cell'),
        ),
        migrations.AlterField(
            model_name='visualcelledit',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]