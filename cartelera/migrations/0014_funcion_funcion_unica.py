# Generated by Django 5.2.4 on 2025-07-13 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cartelera', '0013_alter_funcion_hora'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='funcion',
            constraint=models.UniqueConstraint(fields=('sala_id', 'pelicula_id', 'hora'), name='funcion_unica'),
        ),
    ]
