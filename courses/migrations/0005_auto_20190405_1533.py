# Generated by Django 2.1.7 on 2019-04-05 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_auto_20190405_1430'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='component',
            options={'ordering': ['index']},
        ),
        migrations.AddField(
            model_name='component',
            name='index',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]