# Generated by Django 4.2.9 on 2024-03-19 06:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0014_device_device_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='alarm',
            name='channel',
            field=models.ForeignKey(default=11, on_delete=django.db.models.deletion.CASCADE, to='website.device'),
            preserve_default=False,
        ),
    ]