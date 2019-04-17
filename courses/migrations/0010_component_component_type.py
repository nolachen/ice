# Generated by Django 2.2 on 2019-04-16 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0009_auto_20190416_1332'),
    ]

    operations = [
        migrations.AddField(
            model_name='component',
            name='component_type',
            field=models.CharField(choices=[('TX', 'Text'), ('IM', 'Image')], default='TX', max_length=2),
            preserve_default=False,
        ),
    ]