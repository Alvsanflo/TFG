# Generated by Django 4.2.7 on 2024-06-19 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_juegousuario_ultima_partida_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='juegousuario',
            name='partida_completada',
            field=models.DateField(blank=True, null=True),
        ),
    ]
