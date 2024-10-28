# Generated by Django 5.1.2 on 2024-10-27 04:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_rename_product_outcome_inventory_item'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.category'),
        ),
        migrations.AlterField(
            model_name='product',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.state'),
        ),
    ]