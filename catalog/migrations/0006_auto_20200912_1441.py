# Generated by Django 3.1.1 on 2020-09-12 07:41

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0005_bookinstance_borrower'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookinstance',
            options={'ordering': ['due_back'],
                     'permissions': (('can_mark_returned', 'Set book as returned'),)},
        ),
    ]
