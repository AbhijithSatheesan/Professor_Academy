# Generated by Django 5.0.6 on 2024-06-16 18:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_myusers_marked_colleges'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MarkedColleges',
        ),
    ]
