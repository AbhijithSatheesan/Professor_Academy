# Generated by Django 5.0.6 on 2024-06-16 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('colleges', '0014_remove_colleges_parent_subcategory_and_more'),
        ('users', '0006_markedcolleges_fee_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='myusers',
            name='marked_colleges',
            field=models.ManyToManyField(blank=True, to='colleges.colleges'),
        ),
    ]
