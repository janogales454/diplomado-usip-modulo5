# Generated by Django 5.2.4 on 2025-07-12 19:13

import cartelera.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cartelera', '0006_alter_sala_nombre'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sala',
            name='nombre',
        ),
        migrations.AddField(
            model_name='sala',
            name='nro_sala',
            field=models.CharField(default=django.utils.timezone.now, max_length=10, unique=True, validators=[cartelera.validators.validar_mayor]),
            preserve_default=False,
        ),
    ]
