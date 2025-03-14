# Generated by Django 4.2 on 2024-01-24 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_management', '0004_alter_borrower_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borrowing',
            name='book',
            field=models.ForeignKey(on_delete=models.SET('Removed Book'), to='book_management.book'),
        ),
        migrations.AlterField(
            model_name='borrowing',
            name='borrower',
            field=models.ForeignKey(on_delete=models.SET('Removed Borrower'), to='book_management.borrower'),
        ),
    ]
