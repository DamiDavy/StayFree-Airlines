# Generated by Django 3.1.4 on 2021-01-16 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airlines', '0006_auto_20210110_1818'),
    ]

    operations = [
        migrations.AddField(
            model_name='flight',
            name='price',
            field=models.DecimalField(decimal_places=2, default=50, max_digits=6),
        ),
    ]
