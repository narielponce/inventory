# Generated by Django 5.1.2 on 2024-10-21 18:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.location')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.product')),
            ],
            options={
                'verbose_name_plural': 'Inventories',
            },
        ),
    ]
