# Generated by Django 5.1.2 on 2024-10-27 00:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_remove_product_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='bar_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]