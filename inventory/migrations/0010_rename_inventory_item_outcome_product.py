# Generated by Django 5.1.2 on 2024-10-27 06:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_rename_quantity_outcome_qty'),
    ]

    operations = [
        migrations.RenameField(
            model_name='outcome',
            old_name='inventory_item',
            new_name='product',
        ),
    ]
