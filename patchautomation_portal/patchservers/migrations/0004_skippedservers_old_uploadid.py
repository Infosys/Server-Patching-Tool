# Generated by Django 4.2.7 on 2024-05-02 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patchservers', '0003_rebootuploadmaster'),
    ]

    operations = [
        migrations.AddField(
            model_name='skippedservers',
            name='old_uploadid',
            field=models.TextField(blank=True, null=True),
        ),
    ]
