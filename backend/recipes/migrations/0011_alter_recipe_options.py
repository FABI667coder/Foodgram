# Generated by Django 4.2.4 on 2023-08-27 01:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_alter_recipe_image_alter_tag_color'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-pub_date',), 'verbose_name': 'Рецепты', 'verbose_name_plural': 'Рецепты'},
        ),
    ]
