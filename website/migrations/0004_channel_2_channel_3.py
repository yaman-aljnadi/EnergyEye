# Generated by Django 4.2.9 on 2024-03-04 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_delete_channel'),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel_2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=50)),
                ('device_name', models.CharField(max_length=50)),
                ('connection_type', models.CharField(max_length=30)),
                ('ip_address', models.CharField(max_length=15)),
                ('port_conf', models.CharField(max_length=15)),
                ('signals', models.CharField(max_length=15)),
                ('value1', models.CharField(max_length=15)),
                ('value2', models.CharField(max_length=15)),
                ('value3', models.CharField(max_length=15)),
                ('value4', models.CharField(max_length=15)),
                ('value5', models.CharField(max_length=15)),
                ('value6', models.CharField(max_length=15)),
                ('value7', models.CharField(max_length=15)),
                ('value8', models.CharField(max_length=15)),
                ('value9', models.CharField(max_length=15)),
                ('value10', models.CharField(max_length=15)),
                ('value11', models.CharField(max_length=15)),
                ('value12', models.CharField(max_length=15)),
                ('value13', models.CharField(max_length=15)),
                ('value14', models.CharField(max_length=15)),
                ('value15', models.CharField(max_length=15)),
                ('value16', models.CharField(max_length=15)),
                ('value17', models.CharField(max_length=15)),
                ('value18', models.CharField(max_length=15)),
                ('value19', models.CharField(max_length=15)),
                ('value20', models.CharField(max_length=15)),
                ('value21', models.CharField(max_length=15)),
                ('value22', models.CharField(max_length=15)),
                ('value23', models.CharField(max_length=15)),
                ('value24', models.CharField(max_length=15)),
                ('value25', models.CharField(max_length=15)),
                ('value26', models.CharField(max_length=15)),
                ('value27', models.CharField(max_length=15)),
                ('value28', models.CharField(max_length=15)),
                ('value29', models.CharField(max_length=15)),
                ('value30', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Channel_3',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=50)),
                ('device_name', models.CharField(max_length=50)),
                ('connection_type', models.CharField(max_length=30)),
                ('ip_address', models.CharField(max_length=15)),
                ('port_conf', models.CharField(max_length=15)),
                ('signals', models.CharField(max_length=15)),
                ('value1', models.CharField(max_length=15)),
                ('value2', models.CharField(max_length=15)),
                ('value3', models.CharField(max_length=15)),
                ('value4', models.CharField(max_length=15)),
                ('value5', models.CharField(max_length=15)),
                ('value6', models.CharField(max_length=15)),
                ('value7', models.CharField(max_length=15)),
                ('value8', models.CharField(max_length=15)),
                ('value9', models.CharField(max_length=15)),
                ('value10', models.CharField(max_length=15)),
                ('value11', models.CharField(max_length=15)),
                ('value12', models.CharField(max_length=15)),
                ('value13', models.CharField(max_length=15)),
                ('value14', models.CharField(max_length=15)),
                ('value15', models.CharField(max_length=15)),
                ('value16', models.CharField(max_length=15)),
                ('value17', models.CharField(max_length=15)),
                ('value18', models.CharField(max_length=15)),
                ('value19', models.CharField(max_length=15)),
                ('value20', models.CharField(max_length=15)),
                ('value21', models.CharField(max_length=15)),
                ('value22', models.CharField(max_length=15)),
                ('value23', models.CharField(max_length=15)),
                ('value24', models.CharField(max_length=15)),
                ('value25', models.CharField(max_length=15)),
                ('value26', models.CharField(max_length=15)),
                ('value27', models.CharField(max_length=15)),
                ('value28', models.CharField(max_length=15)),
                ('value29', models.CharField(max_length=15)),
                ('value30', models.CharField(max_length=15)),
            ],
        ),
    ]