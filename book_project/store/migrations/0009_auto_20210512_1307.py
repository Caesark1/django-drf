# Generated by Django 2.2.8 on 2021-05-12 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_userbookrelation_discount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbookrelation',
            name='discount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
    ]
