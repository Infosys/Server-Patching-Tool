# Generated by Django 5.0 on 2024-04-05 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patchservers', '0002_serverrebootdetailsaudit_serverrebootdetails'),
    ]

    operations = [
        migrations.CreateModel(
            name='RebootUploadmaster',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('uploadid', models.TextField(blank=True, null=True)),
                ('uploadedby', models.TextField(blank=True, null=True)),
                ('crref', models.TextField(blank=True, null=True)),
                ('status', models.TextField(blank=True, null=True)),
            ],
        ),
    ]