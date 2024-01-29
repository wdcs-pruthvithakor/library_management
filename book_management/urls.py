
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import requires_csrf_token
from .views import (
    CustomLoginView, CustomSignupView, CustomLogoutView, 
    BorrowerListView, BorrowerCreateView, BorrowerUpdateView, BorrowerDeleteView, BorrowerDetailView,
    BookListView, BookCreateView, BookUpdateView, BookDeleteView, BookDetailView, AvailableBooks,
    BorrowBookView, ReturnBookView, PendingBorrowing, BorrowingDetailsView, BorrowerPendingBrrowingListView,
    BorrowingHistoryView, BorrowerBorrowingHistoryView, AvailableBooksAnoymous,
)

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('signup/', CustomSignupView.as_view(), name='signup'),
    path('borrowers/', BorrowerListView.as_view(), name='borrower_list'),
    path('borrower/create/', BorrowerCreateView.as_view(), name='borrower_create'),
    path('borrower/update/<int:pk>/', BorrowerUpdateView.as_view(), name='borrower_update'),
    path('borrower/delete/<int:pk>/', BorrowerDeleteView.as_view(), name='borrower_delete'),
    path('books/', BookListView.as_view(), name='book_list'),
    path('book/create/', BookCreateView.as_view(), name='book_create'),
    path('book/update/<int:pk>/', BookUpdateView.as_view(), name='book_update'),
    path('book/delete/<int:pk>/', BookDeleteView.as_view(), name='book_delete'),
    path('book/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('borrower/<int:pk>/', BorrowerDetailView.as_view(), name='borrower_detail'),
    path('available/', AvailableBooks.as_view(), name='available_books'),
    path('available_anonymous/', AvailableBooksAnoymous.as_view(), name='available_books_anonymous'),
    path('borrow/', BorrowBookView.as_view(), name='borrow_book'),
    path('return/', ReturnBookView.as_view(), name='return_book'),
    path('pending/', PendingBorrowing.as_view(), name='pending_borrowing'),
    path('borrowing/<int:pk>/', BorrowingDetailsView.as_view(), name='borrowing_detail'),
    path('borrower/pending/', BorrowerPendingBrrowingListView.as_view(), name='borrower_pending_borrowing'),
    path('history/', BorrowingHistoryView.as_view(), name='borrowing_history'),
    path('borrower/history/', BorrowerBorrowingHistoryView.as_view(), name='borrower_borrowing_history'),
]
