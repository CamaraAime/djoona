# Generated by Django 5.1.3 on 2024-12-13 12:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djona_admin', '0013_alter_produit_image_alter_reservation_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='produit',
            name='annee',
        ),
        migrations.RemoveField(
            model_name='produit',
            name='etat',
        ),
        migrations.RemoveField(
            model_name='produit',
            name='ville',
        ),
    ]