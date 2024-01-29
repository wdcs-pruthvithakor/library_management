from typing import Any
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import user_passes_test
from django.db.models.query import QuerySet
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.db.models import Q, Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, FormView, DeleteView, View, DetailView
from datetime import datetime
from .models import Book, Borrower, Borrowing
from .forms import BookForm, BorrowerForm, CustomSignupForm, CustomLoginForm

def is_library_staff(user):
    return user.is_authenticated and (user.is_staff)

class LibrarianRequiredMixin(LoginRequiredMixin):

    @method_decorator(user_passes_test(is_library_staff))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class BookListView(LibrarianRequiredMixin, ListView):
    model = Book
    template_name = 'book_list.html'
    paginate_by = 8
    ordering = ['title']
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        order_by = self.request.GET.get('order_by', 'title')
        dir = self.request.GET.get('dir', 'asc')

        queryset = super().get_queryset()

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(availability_status__icontains=query)
            )

        if order_by:
            if dir == 'asc':
                queryset = queryset.order_by(order_by)
            elif dir == 'desc':
                queryset = queryset.order_by(f'-{order_by}')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_by'] = self.request.GET.get('order_by', 'title')
        context['dir'] = self.request.GET.get('dir', 'asc')
        context['search_query'] = self.request.GET.get('q')
        return context

class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'book_detail.html'
    context_object_name = 'book'

class BookCreateView(LibrarianRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'book_form.html'
    success_url = reverse_lazy('book_list')

    def form_valid(self, form):
        # Do something with the form data (e.g., save to the database)
        response = super().form_valid(form)

        # Add a success message
        messages.success(self.request, 'Book created successfully.', extra_tags='bg-success')

        return response

class BookUpdateView(LibrarianRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'book_form.html'
    success_url = reverse_lazy('book_list')

    def form_valid(self, form):
        # Do something with the form data (e.g., save to the database)
        response = super().form_valid(form)
        obj = self.get_object()
        # Add a success message
        messages.success(self.request, f'Book {obj.title.upper()} Updated successfully.', extra_tags='bg-success')

        return response

class BookDeleteView(LibrarianRequiredMixin, DeleteView):
    model = Book
    template_name = 'book_confirm_delete.html'
    success_url = reverse_lazy('book_list')

    def get_success_url(self):
        return super().get_success_url()

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            messages.success(self.request, f'Book has been deleted successfully.', extra_tags='bg-success')
            return response
        except ValidationError as e:
            # Handle the validation error, e.g., display a message to the user
            for i in e:
                messages.error(self.request, str(i), extra_tags='bg-danger')
            return redirect('book_list')
class BorrowerListView(LibrarianRequiredMixin, ListView):
    model = Borrower
    template_name = 'borrower_list.html'
    paginate_by = 5
    ordering = ['name']
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        order_by = self.request.GET.get('order_by', 'name')
        dir = self.request.GET.get('dir', 'asc')

        queryset = super().get_queryset().select_related('user')

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
            )

        if order_by:
            if dir == 'asc':
                queryset = queryset.order_by(order_by)
            elif dir == 'desc':
                queryset = queryset.order_by(f'-{order_by}')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_by'] = self.request.GET.get('order_by', 'name')
        context['dir'] = self.request.GET.get('dir', 'asc')
        context['search_query'] = self.request.GET.get('q')
        return context
    
class BorrowerDetailView(LibrarianRequiredMixin, DetailView):
    model = Borrower
    template_name = 'borrower_detail.html'
    context_object_name = 'borrower'

class BorrowerCreateView(LibrarianRequiredMixin, CreateView):
    model = Borrower
    form_class = BorrowerForm
    template_name = 'borrower_form.html'
    success_url = reverse_lazy('borrower_list')

    def form_valid(self, form):
        # Do something with the form data (e.g., save to the database)
        response = super().form_valid(form)

        # Add a success message
        messages.success(self.request, 'Borrower created successfully.', extra_tags='bg-success')

        return response

class BorrowerUpdateView(LibrarianRequiredMixin, UpdateView):
    model = Borrower
    form_class = BorrowerForm
    template_name = 'borrower_form.html'
    success_url = reverse_lazy('borrower_list')

    def form_valid(self, form):
        # Do something with the form data (e.g., save to the database)
        response = super().form_valid(form)
        obj = self.get_object()
        # Add a success message
        messages.success(self.request, f'Borrower {obj.name.upper()} Updated successfully.', extra_tags='bg-success')

        return response
    
class BorrowerDeleteView(LibrarianRequiredMixin, DeleteView):
    model = Borrower
    template_name = 'borrower_confirm_delete.html'
    success_url = reverse_lazy('borrower_list')

    def get_success_url(self):
        
        return super().get_success_url()
    
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            messages.success(self.request, f'Borrower has been deleted successfully.', extra_tags='bg-success')
            return response
        except ValidationError as e:
            for i in e:
                messages.error(self.request, str(i), extra_tags='bg-danger')
            return redirect('borrower_list')

class AvailableBooks(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Book
    template_name = 'available_books.html'
    paginate_by = 5
    ordering = ['title']
    permission_required = ('book_management.can_borrow', 'book_management.can_return')
    raise_exception = False

    def handle_no_permission(self):
        if self.raise_exception:
            return super().handle_no_permission()

        messages.error(self.request, 'You do not have permission to access this page.', extra_tags='bg-danger')
        return self.redirect_to_login()

    def redirect_to_login(self):
        return redirect(reverse_lazy('login'))

    def get_queryset(self):
        query = self.request.GET.get('q')
        order_by = self.request.GET.get('order_by', 'title')
        dir = self.request.GET.get('dir', 'asc')

        queryset = super().get_queryset().filter(availability_status=True)

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query)
            )

        if order_by:
            if dir == 'asc':
                queryset = queryset.order_by(order_by)
            elif dir == 'desc':
                queryset = queryset.order_by(f'-{order_by}')

        return queryset
    
class AvailableBooksAnoymous(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'available_books_anonymous.html'
    paginate_by = 5
    ordering = ['title']

    def get_queryset(self):
        query = self.request.GET.get('q')
        order_by = self.request.GET.get('order_by', 'title')
        dir = self.request.GET.get('dir', 'asc')

        queryset = super().get_queryset().filter(availability_status=True)

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query)
            )

        if order_by:
            if dir == 'asc':
                queryset = queryset.order_by(order_by)
            elif dir == 'desc':
                queryset = queryset.order_by(f'-{order_by}')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_by'] = self.request.GET.get('order_by', 'title')
        context['dir'] = self.request.GET.get('dir', 'asc')
        
        return context
    
class BorrowBookView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ('book_management.can_borrow')
    raise_exception = False

    def handle_no_permission(self):
        if self.raise_exception:
            return super().handle_no_permission()

        messages.error(self.request, 'You do not have permission to access this page.', extra_tags='bg-danger')
        return self.redirect_to_login()

    def redirect_to_login(self):
        return redirect(reverse_lazy('login'))
    
    def post(self, request, *args, **kwargs):
        book_id = request.POST.get('book_id')
        username = request.POST.get('username')
        book = Book.objects.get(pk=book_id)
        user = User.objects.get(username=username)
        borrower = Borrower.objects.get(user=user)
        if book and user:
            book = Book.objects.get(pk=book_id)
            if book.availability_status:
                borrowing = Borrowing.objects.create(borrower=borrower, book=book, borrow_date=datetime.now())
                book.availability_status = False
                book.save()
                messages.success(request, f'Book borrowed successfully. borrowing_id: {str(borrowing.id)}',extra_tags='bg-success')
            else:
                messages.error(request, 'Book is not available.', extra_tags='bg-danger')
        return redirect('available_books')

class ReturnBookView(LoginRequiredMixin, PermissionRequiredMixin,View):
    permission_required = ('book_management.can_return')
    raise_exception = False

    def handle_no_permission(self):
        if self.raise_exception:
            return super().handle_no_permission()

        messages.error(self.request, 'You do not have permission to access this page.', extra_tags='bg-danger')
        return self.redirect_to_login()

    def redirect_to_login(self):
        return redirect(reverse_lazy('login'))

    def post(self, request, *args, **kwargs):
        borrowing_id = request.POST.get('borrowing_id')
        borrowing = Borrowing.objects.filter(pk=borrowing_id).exists()
        if borrowing:
            borrowing = Borrowing.objects.get(pk=borrowing_id)
            book = borrowing.book
            book.availability_status = True
            book.save()
            borrowing.return_date = datetime.now()
            borrowing.save()
            messages.success(request, 'Book returned successfully.', extra_tags='bg-success')
        else:
            messages.error(request, 'Book is not borrowed.', extra_tags='bg-danger')
        return redirect('borrower_pending_borrowing')

class PendingBorrowing(LibrarianRequiredMixin, ListView):
    model = Borrowing
    template_name = 'pending_borrowings.html'
    paginate_by = 5
    ordering = ['borrow_date']

    def get_queryset(self):
        query = self.request.GET.get('q')
        order_by = self.request.GET.get('order_by', 'borrow_date')
        dir = self.request.GET.get('dir', 'asc')

        queryset = super().get_queryset().filter(return_date__isnull=True)

        if query:
            queryset = queryset.filter(
                Q(borrower__name__icontains=query) |
                Q(book__title__icontains=query)
            )

        if order_by:
            if dir == 'asc':
                queryset = queryset.order_by(order_by)
            elif dir == 'desc':
                queryset = queryset.order_by(f'-{order_by}')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_by'] = self.request.GET.get('order_by', 'borrow_date')
        context['dir'] = self.request.GET.get('dir', 'asc')
        return context
    
class BorrowerPendingBrrowingListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Borrowing
    template_name = 'borrower_pending_borrowings.html'
    paginate_by = 5
    ordering = ['borrow_date']
    permission_required = ('book_management.can_borrow', 'book_management.can_return')
    raise_exception = False

    def get(self, request, *args, **kwargs):
        if not self.has_permission():
            return self.handle_no_permission()

        return super().get(request, *args, **kwargs)

    def handle_no_permission(self):
        if self.raise_exception:
            return super().handle_no_permission()

        messages.error(self.request, 'You do not have permission to access this page.', extra_tags='bg-danger')
        return self.redirect_to_login()

    def redirect_to_login(self):
        return redirect(reverse_lazy('login'))

    def get_queryset(self):
        query = self.request.GET.get('q')
        order_by = self.request.GET.get('order_by', 'borrow_date')
        dir = self.request.GET.get('dir', 'asc')
        borrower = Borrower.objects.get(user=self.request.user)
        queryset = super().get_queryset().filter(return_date__isnull=True, borrower=borrower)

        if query:
            queryset = queryset.filter(
                Q(borrower__name__icontains=query) |
                Q(book__title__icontains=query)
            )

        if order_by:
            if dir == 'asc':
                queryset = queryset.order_by(order_by)
            elif dir == 'desc':
                queryset = queryset.order_by(f'-{order_by}')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_by'] = self.request.GET.get('order_by', 'borrow_date')
        context['dir'] = self.request.GET.get('dir', 'asc')
        return context
    
class BorrowingHistoryView(LibrarianRequiredMixin, ListView):
    model = Borrowing
    template_name = 'borrowing_history.html'
    paginate_by = 5
    ordering = ['borrow_date']

    def get_queryset(self):
        query = self.request.GET.get('q')
        order_by = self.request.GET.get('order_by', 'borrow_date')
        dir = self.request.GET.get('dir', 'asc')

        queryset = super().get_queryset().filter(return_date__isnull=False)

        if query:
            queryset = queryset.filter(
                Q(borrower__name__icontains=query) |
                Q(book__title__icontains=query)
            )

        if order_by:
            if dir == 'asc':
                queryset = queryset.order_by(order_by)
            elif dir == 'desc':
                queryset = queryset.order_by(f'-{order_by}')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_by'] = self.request.GET.get('order_by', 'borrow_date')
        context['dir'] = self.request.GET.get('dir', 'asc')
        return context

class BorrowerBorrowingHistoryView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Borrowing
    template_name = 'borrowing_history.html'
    paginate_by = 5
    ordering = ['borrow_date']
    permission_required = ('book_management.can_borrow', 'book_management.can_return')
    raise_exception = False

    def get(self, request, *args, **kwargs):
        if not self.has_permission():
            return self.handle_no_permission()

        return super().get(request, *args, **kwargs)

    def handle_no_permission(self):
        if self.raise_exception:
            return super().handle_no_permission()

        messages.error(self.request, 'You do not have permission to access this page.', extra_tags='bg-danger')
        return self.redirect_to_login()

    def redirect_to_login(self):
        return redirect(reverse_lazy('login'))

    def get_queryset(self):
        query = self.request.GET.get('q')
        order_by = self.request.GET.get('order_by', 'borrow_date')
        dir = self.request.GET.get('dir', 'asc')
        borrower = Borrower.objects.get(user=self.request.user)

        queryset = super().get_queryset().filter(return_date__isnull=False, borrower=borrower)

        if query:
            queryset = queryset.filter(
                Q(book__title__icontains=query)
            )

        if order_by:
            if dir == 'asc':
                queryset = queryset.order_by(order_by)
            elif dir == 'desc':
                queryset = queryset.order_by(f'-{order_by}')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_by'] = self.request.GET.get('order_by', 'borrow_date')
        context['dir'] = self.request.GET.get('dir', 'asc')
        return context

class BorrowingDetailsView(LoginRequiredMixin, DetailView):
    model = Borrowing
    template_name = 'borrowing_detail.html'
    context_object_name = 'borrowing'

class CustomSignupView(FormView):
    template_name = 'signup.html'
    form_class = CustomSignupForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Account created successfully.', extra_tags='bg-success')
        return super().form_valid(form)

class CustomLoginView(FormView):
    template_name = 'login.html'
    form_class = CustomLoginForm
    success_url = reverse_lazy('book_list')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Logged in successfully.', extra_tags='bg-success')
        return super().form_valid(form)
    
    def get_success_url(self):
        # Check if the user is a staff user
        if self.request.user.is_staff:
            return reverse_lazy('book_list')  # Replace with your staff dashboard URL
        elif self.request.user.has_perm('book_management.can_borrow') and self.request.user.has_perm('book_management.can_return'):
            return reverse_lazy('available_books')
        else:
            return reverse_lazy('available_books_anonymous') 

class CustomLogoutView(View):
    
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'Logged out successfully.', extra_tags='bg-success')
        return redirect('login')