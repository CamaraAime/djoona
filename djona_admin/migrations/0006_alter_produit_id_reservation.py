# Generated by Django 5.1.3 on 2024-12-12 13:13

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djona_admin', '0005_etatvehicule_produit_delete_brand_delete_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produit',
            name='id',
            field=models.CharField(max_length=255, primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('client_nom', models.CharField(max_length=255)),
                ('client_prenom', models.CharField(max_length=255)),
                ('client_email', models.EmailField(max_length=254)),
                ('client_telephone', models.CharField(max_length=20)),
                ('adresse', models.CharField(max_length=255)),
                ('date_debut', models.DateField()),
                ('duree', models.PositiveIntegerField()),
                ('date_fin', models.DateField(editable=False)),
                ('date_reservation', models.DateTimeField(default=django.utils.timezone.now)),
                ('produit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='djona_admin.produit')),
            ],
            options={
                'verbose_name': 'Réservation',
                'verbose_name_plural': 'Réservations',
                'ordering': ['-date_reservation'],
            },
        ),
    ]