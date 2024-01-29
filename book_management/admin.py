from django.contrib import admin
from .models import Book, Borrower, Borrowing


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    class Meta:
        model = Book
        fields = '__all__'


@admin.register(Borrower)
class BorrowerAdmin(admin.ModelAdmin):
    class Meta:
        model = Borrower
        fields = '__all__'


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    class Meta:
        model = Borrowing
        fields = '__all__'
