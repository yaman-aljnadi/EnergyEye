# Generated by Django 4.2.9 on 2024-05-28 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0030_remove_alarmtrigger_trigger_function'),
    ]

    operations = [
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('encrypted_license_key', models.CharField(max_length=255, unique=True)),
                ('max_devices', models.IntegerField(default=40)),
            ],
        ),
    ]