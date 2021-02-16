# Generated by Django 3.1.4 on 2021-01-10 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airlines', '0003_auto_20210110_1732'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flight',
            name='when',
        ),
        migrations.AddField(
            model_name='current',
            name='flights',
            field=models.ManyToManyField(blank=True, to='airlines.Flight'),
        ),
        migrations.AlterField(
            model_name='flight',
            name='duration',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='flight',
            name='passengers',
            field=models.ManyToManyField(blank=True, to='airlines.Passenger'),
        ),
    ]
