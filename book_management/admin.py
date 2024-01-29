"""
Admin models for library_management application.
"""
from django.contrib import admin
from .models import Book, Borrower, Borrowing


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Admin class for Book model.
    """
    class Meta:
        """
        Meta class for the BookAdmin.
        """
        model = Book
        fields = '__all__'


@admin.register(Borrower)
class BorrowerAdmin(admin.ModelAdmin):
    """
    Admin class for Borrower model.
    """
    class Meta:
        """
        Meta class for the BorrowerAdmin.
        """
        model = Borrower
        fields = '__all__'


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    """
    Admin class for Borrowing model.
    """
    class Meta:
        """
        Meta class for the BorrowingAdmin.
        """
        model = Borrowing
        fields = '__all__'
