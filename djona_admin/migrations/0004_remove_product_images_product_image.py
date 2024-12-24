# Generated by Django 5.1.3 on 2024-12-09 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djona_admin', '0003_brand'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='images',
        ),
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(default=255, upload_to='image/'),
            preserve_default=False,
        ),
    ]