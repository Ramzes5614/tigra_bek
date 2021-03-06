# Generated by Django 2.2.17 on 2021-02-04 14:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('verification', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='phonemodel',
            options={'verbose_name': 'Телефон', 'verbose_name_plural': 'Телефоны'},
        ),
        migrations.AlterField(
            model_name='phonemodel',
            name='phone_number',
            field=models.CharField(default='+999999999', max_length=15, unique=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')], verbose_name='Телефон'),
        ),
    ]
