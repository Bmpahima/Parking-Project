# Generated by Django 5.1.4 on 2025-01-24 12:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkingApp', '0008_parkingauth'),
        ('parkingAuth', '0002_parkingauth_is_active_parkingauth_is_admin'),
    ]

    operations = [
        migrations.DeleteModel(
            name='parkingAuth',
        ),
        migrations.AddField(
            model_name='parking',
            name='driver',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='parking', to='parkingAuth.parkingauth'),
        ),
        migrations.AddField(
            model_name='parking',
            name='is_saved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='parking',
            name='reserved_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
