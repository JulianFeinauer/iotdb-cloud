# Generated by Django 3.2.6 on 2021-08-21 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iotdb_cloud_core', '0003_auto_20210821_1902'),
    ]

    operations = [
        migrations.AddField(
            model_name='iotdbrelease',
            name='admin_password',
            field=models.TextField(default='asdf'),
            preserve_default=False,
        ),
    ]
