# Generated by Django 4.2.9 on 2024-04-20 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0020_alarm_alarm_triggered_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='register',
            name='polling_interval',
            field=models.CharField(default='1', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='alarm',
            name='alarm_triggered_at',
            field=models.CharField(default='', max_length=50),
        ),
    ]