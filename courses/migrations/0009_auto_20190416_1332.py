# Generated by Django 2.2 on 2019-04-16 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0008_auto_20190407_0853'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagecomponent',
            name='image',
            field=models.ImageField(default='no image', upload_to='images/'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='imagecomponent',
            name='image_details',
            field=models.TextField(),
        ),
    ]
