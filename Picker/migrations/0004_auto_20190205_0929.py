# Generated by Django 2.1.5 on 2019-02-05 09:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Picker', '0003_auto_20190205_0917'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='recipe',
            unique_together={('dish', 'ingredient')},
        ),
    ]
