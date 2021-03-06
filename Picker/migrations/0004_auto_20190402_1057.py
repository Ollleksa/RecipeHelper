# Generated by Django 2.1.5 on 2019-04-02 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Picker', '0003_auto_20190402_0652'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='carbohydrate',
            field=models.DecimalField(blank=True, decimal_places=3, default=None, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='energy',
            field=models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=7, null=True),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='fats',
            field=models.DecimalField(blank=True, decimal_places=3, default=None, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='proteins',
            field=models.DecimalField(blank=True, decimal_places=3, default=0.0, max_digits=6, null=True),
        ),
    ]
