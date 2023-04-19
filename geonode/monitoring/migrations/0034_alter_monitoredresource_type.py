# Generated by Django 3.2.18 on 2023-04-19 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0033_alter_monitoredresource_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitoredresource',
            name='type',
            field=models.CharField(choices=[('', 'No resource'), ('dataset', 'Dataset'), ('layer', 'Layer'), ('map', 'Map'), ('resource_base', 'Resource base'), ('document', 'Document'), ('style', 'Style'), ('admin', 'Admin'), ('url', 'URL'), ('other', 'Other')], default='', max_length=255),
        ),
    ]
