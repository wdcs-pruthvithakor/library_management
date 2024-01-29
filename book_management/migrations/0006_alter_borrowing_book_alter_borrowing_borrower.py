# Generated by Django 4.2 on 2024-01-24 09:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('book_management', '0005_alter_borrowing_book_alter_borrowing_borrower'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borrowing',
            name='book',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='book_management.book'),
        ),
        migrations.AlterField(
            model_name='borrowing',
            name='borrower',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='book_management.borrower'),
        ),
    ]
