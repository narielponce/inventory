# Generated by Django 5.1.2 on 2024-10-27 06:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_rename_inventory_item_outcome_product'),
    ]

    operations = [
        migrations.RenameField(
            model_name='outcome',
            old_name='product',
            new_name='inventory',
        ),
    ]
