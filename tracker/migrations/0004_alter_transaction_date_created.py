# Generated by Django 5.1.7 on 2025-03-26 08:12

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tracker", "0003_alter_transaction_transaction_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="date_created",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
