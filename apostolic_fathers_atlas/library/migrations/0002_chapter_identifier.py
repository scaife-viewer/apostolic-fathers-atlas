# Generated by Django 2.2.3 on 2019-08-30 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='identifier',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
    ]
