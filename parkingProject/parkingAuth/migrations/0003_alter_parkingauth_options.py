# Generated by Django 5.1.4 on 2025-01-27 18:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parkingAuth', '0002_parkingauth_is_active_parkingauth_is_admin'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='parkingauth',
            options={'verbose_name': 'User Name'},
        ),
    ]
