# Generated by Django 5.1.2 on 2024-10-23 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_income_outcome'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='serial_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
