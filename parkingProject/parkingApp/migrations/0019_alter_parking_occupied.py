# Generated by Django 5.1.4 on 2025-03-29 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkingApp', '0018_parking_unauthorized_notification_sent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parking',
            name='occupied',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
