# Generated by Django 5.1.3 on 2024-12-19 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djona_admin', '0021_carouselimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carouselimage',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='carouselimage',
            name='image',
        ),
        migrations.AddField(
            model_name='carouselimage',
            name='image_url',
            field=models.URLField(default=1),
            preserve_default=False,
        ),
    ]