# Generated by Django 2.2.8 on 2021-05-12 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_auto_20210512_1307'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userbookrelation',
            name='discount',
        ),
        migrations.AddField(
            model_name='book',
            name='discount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
    ]
