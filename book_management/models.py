# models.py

from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.core.exceptions import ValidationError

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    ISBN = models.CharField(max_length=13, unique=True)
    publication_date = models.DateField()
    availability_status = models.BooleanField(default=True)
    
    def has_pending_returns(self):
        # Check if the book has any pending returns
        return self.borrowing_set.filter(return_date__isnull=True).exists()

    def delete(self, *args, **kwargs):
        if self.has_pending_returns():
            raise ValidationError("Cannot delete book with pending returns.")
        return super().delete(*args, **kwargs)


class Borrower(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)

    def has_pending_returns(self):
        # Check if the borrower has any pending returns
        return self.borrowing_set.filter(return_date__isnull=True).exists()

    def delete(self, *args, **kwargs):
        if self.has_pending_returns():
            raise ValidationError("Cannot delete borrower with pending returns.")
        return super().delete(*args, **kwargs)

class Borrowing(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.SET_NULL, null=True)
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    borrow_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    
    class Meta:
        permissions = [
            ("can_borrow", "Can borrow books"),
            ("can_return", "Can return books"),           
            ]
