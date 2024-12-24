# Generated by Django 5.1.3 on 2024-12-13 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djona_admin', '0010_rename_caractere_produit_duree_produit_etat'),
    ]

    operations = [
        migrations.RenameField(
            model_name='produit',
            old_name='duree',
            new_name='ville',
        ),
        migrations.AddField(
            model_name='produit',
            name='annee',
            field=models.CharField(default=1, max_length=4),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='etatvehicule',
            name='date_ajout',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='produit',
            name='kilometrage',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='produit',
            name='prix',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='produit',
            name='prix_location',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]