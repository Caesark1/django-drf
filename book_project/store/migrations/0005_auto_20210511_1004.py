# Generated by Django 2.2.8 on 2021-05-11 10:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_userbookrelation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userbookrelation',
            old_name='in_bookmargs',
            new_name='in_bookmarks',
        ),
    ]
