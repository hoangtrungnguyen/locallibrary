# Generated by Django 3.1.1 on 2020-09-09 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='language',
            field=models.CharField(default='en', help_text="This book's language", max_length=4),
        ),
    ]
