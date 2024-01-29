"""
Models for library_management application.
"""

from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.core.exceptions import ValidationError

class Book(models.Model):
    """
    Model for books.
    """
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    ISBN = models.CharField(max_length=13, unique=True)
    publication_date = models.DateField()
    availability_status = models.BooleanField(default=True)
    
    def has_pending_returns(self):
        """
        Check if there are any pending returns for the borrowing set.
        """
        return self.borrowing_set.filter(return_date__isnull=True).exists()

    def delete(self, *args, **kwargs):
        """
        Deletes the object. If the object has pending returns, raises a ValidationError.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The return value of the super's delete method.
        """
        if self.has_pending_returns():
            raise ValidationError("Cannot delete book with pending returns.")
        return super().delete(*args, **kwargs)


class Borrower(models.Model):
    """
    Model for borrowers.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)

    def has_pending_returns(self):
        """
        Check if the borrower has any pending returns
        """
        return self.borrowing_set.filter(return_date__isnull=True).exists()

    def delete(self, *args, **kwargs):
        """
        Delete the object, but first check if there are pending returns for the borrower.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            The result of the super class' delete method.
        """
        if self.has_pending_returns():
            raise ValidationError("Cannot delete borrower with pending returns.")
        return super().delete(*args, **kwargs)

class Borrowing(models.Model):
    """
    Model for borrowing books.
    """
    borrower = models.ForeignKey(Borrower, on_delete=models.SET_NULL, null=True)
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    borrow_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    
    class Meta:
        """
        Meta class for the Borrowing model.
        """
        permissions = [
            ("can_borrow", "Can borrow books"),
            ("can_return", "Can return books"),           
            ]
