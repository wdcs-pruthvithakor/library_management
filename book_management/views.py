"""
Views for library_management application.
"""
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
    """
    Check if the user is authenticated and is a staff member.
    :param user: User object
    :return: Boolean indicating if the user is a staff member
    """
    return user.is_authenticated and (user.is_staff)

class LibrarianRequiredMixin(LoginRequiredMixin):

    @method_decorator(user_passes_test(is_library_staff))
    def dispatch(self, request, *args, **kwargs):
        """
        Dispatches the request to the appropriate handler method. 

        Args:
            request: The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The response from the super class's dispatch method.
        """
        return super().dispatch(request, *args, **kwargs)

class BookListView(LibrarianRequiredMixin, ListView):
    """
    View for displaying a list of books. It checks if the user has permission to access the page.
    """
    model = Book
    template_name = 'book_list.html'
    paginate_by = 8
    ordering = ['title']
    
    def get_queryset(self):
        """
        Return the queryset after filtering based on the request parameters 'q', 'order_by', and 'dir'.
        """
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
        """
        Return the context data with additional order_by, dir, and search_query parameters.
        """
        context = super().get_context_data(**kwargs)
        context['order_by'] = self.request.GET.get('order_by', 'title')
        context['dir'] = self.request.GET.get('dir', 'asc')
        context['search_query'] = self.request.GET.get('q')
        return context

class BookDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying details of a single book.
    """
    model = Book
    template_name = 'book_detail.html'
    context_object_name = 'book'

class BookCreateView(LibrarianRequiredMixin, CreateView):
    """
    View for creating a new book. It checks if the user has permission to access the page.
    """
    model = Book
    form_class = BookForm
    template_name = 'book_form.html'
    success_url = reverse_lazy('book_list')

    def form_valid(self, form):
        """
        Check if the form is valid and return the response.
        :param form: the form to be validated
        :return: the response after the form validation
        """
        
        response = super().form_valid(form)
   
        messages.success(self.request, 'Book created successfully.', extra_tags='bg-success')

        return response

class BookUpdateView(LibrarianRequiredMixin, UpdateView):
    """
    View for updating an existing book. It checks if the user has permission to access the page.
    """
    model = Book
    form_class = BookForm
    template_name = 'book_form.html'
    success_url = reverse_lazy('book_list')

    def form_valid(self, form):
        """
        Check if the form is valid, then perform some actions and return the response.
        """
        
        response = super().form_valid(form)
        obj = self.get_object()
        
        messages.success(self.request, f'Book {obj.title.upper()} Updated successfully.', extra_tags='bg-success')

        return response

class BookDeleteView(LibrarianRequiredMixin, DeleteView):
    """
    View for deleting an existing book. It checks if the user has permission to access the page.
    """
    model = Book
    template_name = 'book_confirm_delete.html'
    success_url = reverse_lazy('book_list')

    def get_success_url(self):
        """
        Return the success URL for the current request. 
        """
        return super().get_success_url()

    def post(self, request, *args, **kwargs):
        """
        Handle the HTTP POST request, call the parent class's post method, display a success message, and handle validation errors.
        """
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
    """
    View for displaying a list of borrowers. It checks if the user has permission to access the page.
    """
    model = Borrower
    template_name = 'borrower_list.html'
    paginate_by = 5
    ordering = ['name']
    
    def get_queryset(self):
        """
        Retrieves the queryset based on the request parameters.

        Returns:
            QuerySet: The filtered and ordered queryset based on the request parameters.
        """
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
        """
        Return the context data for the view, including order_by, dir, and search_query.
        """
        context = super().get_context_data(**kwargs)
        context['order_by'] = self.request.GET.get('order_by', 'name')
        context['dir'] = self.request.GET.get('dir', 'asc')
        context['search_query'] = self.request.GET.get('q')
        return context
    
class BorrowerDetailView(LibrarianRequiredMixin, DetailView):
    """
    View for displaying details of a single borrower. It checks if the user has permission to access the page.
    """
    model = Borrower
    template_name = 'borrower_detail.html'
    context_object_name = 'borrower'

class BorrowerCreateView(LibrarianRequiredMixin, CreateView):
    """
    View for creating a new borrower. It checks if the user has permission to access the page.
    """
    model = Borrower
    form_class = BorrowerForm
    template_name = 'borrower_form.html'
    success_url = reverse_lazy('borrower_list')

    def form_valid(self, form):
        """
        Check if the form is valid and return the response.
        """
        
        response = super().form_valid(form)

        messages.success(self.request, 'Borrower created successfully.', extra_tags='bg-success')

        return response

class BorrowerUpdateView(LibrarianRequiredMixin, UpdateView):
    """
    View for updating an existing borrower. It checks if the user has permission to access the page.
    """
    model = Borrower
    form_class = BorrowerForm
    template_name = 'borrower_form.html'
    success_url = reverse_lazy('borrower_list')

    def form_valid(self, form):
        """
        Validates the form and updates the borrower's name successfully. 

        Args:
            form: The form to be validated.

        Returns:
            The response from the super class after validating the form.
        """
        
        response = super().form_valid(form)
        obj = self.get_object()
        
        messages.success(self.request, f'Borrower {obj.name.upper()} Updated successfully.', extra_tags='bg-success')

        return response
    
class BorrowerDeleteView(LibrarianRequiredMixin, DeleteView):
    """
    View for deleting an existing borrower. It checks if the user has permission to access the page.
    """
    model = Borrower
    template_name = 'borrower_confirm_delete.html'
    success_url = reverse_lazy('borrower_list')

    def get_success_url(self):
        """
        Return the success URL for the view.
        """
        
        return super().get_success_url()
    
    def post(self, request, *args, **kwargs):
        """
        Handle HTTP POST request, call super().post with request, args, and kwargs, 
        display success message, and handle validation error by displaying error 
        messages and redirecting to borrower_list.
        """
        try:
            response = super().post(request, *args, **kwargs)
            messages.success(self.request, f'Borrower has been deleted successfully.', extra_tags='bg-success')
            return response
        except ValidationError as e:
            for i in e:
                messages.error(self.request, str(i), extra_tags='bg-danger')
            return redirect('borrower_list')

class AvailableBooks(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    View for displaying a list of available books. It checks if the user has permission to access the page.
    """
    model = Book
    template_name = 'available_books.html'
    paginate_by = 5
    ordering = ['title']
    permission_required = ('book_management.can_borrow', 'book_management.can_return')
    raise_exception = False

    def handle_no_permission(self):
        """
        Handles the case when the user does not have permission. If self.raise_exception is True,
        calls super().handle_no_permission(). Otherwise, displays an error message and redirects
        the user to the login page.
        """
        if self.raise_exception:
            return super().handle_no_permission()

        messages.error(self.request, 'You do not have permission to access this page.', extra_tags='bg-danger')
        return self.redirect_to_login()

    def redirect_to_login(self):
        """
        Redirects to the login page.
        """
        return redirect(reverse_lazy('login'))

    def get_queryset(self):
        """
        Returns the filtered queryset based on the request parameters.

        Parameters:
            self: The instance of the class.
        
        Returns:
            queryset: The filtered queryset based on the request parameters.
        """
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
    """
    View for displaying a list of available books for Users that are not borrower or staff.
    """
    model = Book
    template_name = 'available_books_anonymous.html'
    paginate_by = 5
    ordering = ['title']

    def get_queryset(self):
        """
        Returns a filtered queryset based on the request parameters.

        Parameters:
            self: The instance of the class.
        
        Returns:
            queryset: A filtered queryset based on the request parameters.
        """
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
        """
        Get the context data for the view.

        :param kwargs: additional keyword arguments
        :return: the context data for the view
        """
        context = super().get_context_data(**kwargs)
        context['order_by'] = self.request.GET.get('order_by', 'title')
        context['dir'] = self.request.GET.get('dir', 'asc')
        
        return context
    
class BorrowBookView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    View for borrowing a book. It checks if user have permission to borrow book.
    """
    permission_required = ('book_management.can_borrow')
    raise_exception = False

    def handle_no_permission(self):
        """
        Handle the case where the user has no permission to access a page.

        No parameters.

        Returns:
            The result of redirecting to the login page.
        """
        if self.raise_exception:
            return super().handle_no_permission()

        messages.error(self.request, 'You do not have permission to access this page.', extra_tags='bg-danger')
        return self.redirect_to_login()

    def redirect_to_login(self):
        """
        Redirects to the login page.
        This function does not take any parameters.
        It returns a redirection to the 'login' URL.
        """
        return redirect(reverse_lazy('login'))
    
    def post(self, request, *args, **kwargs):
        """
        Handle the POST request to borrow a book, check availability, and create a borrowing record.
        :param self: The class instance
        :param request: The HTTP request object
        :param args: Additional positional arguments
        :param kwargs: Additional keyword arguments
        :return: Redirect to the 'available_books' URL
        """
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
    """
    View for returning a borrowed book. It checks if user have permission to return book.
    """
    permission_required = ('book_management.can_return')
    raise_exception = False

    def handle_no_permission(self):
        """
        Handle the case when the user has no permission to access a page. 
        If raise_exception is False, display an error message and redirect to the login page.
        """
        if self.raise_exception:
            return super().handle_no_permission()

        messages.error(self.request, 'You do not have permission to access this page.', extra_tags='bg-danger')
        return self.redirect_to_login()

    def redirect_to_login(self):
        """
        Redirects to the login page.
        """
        return redirect(reverse_lazy('login'))

    def post(self, request, *args, **kwargs):
        """
        Handles the POST request to return a borrowed book. 
        :param request: The HTTP request object
        :param args: Additional positional arguments
        :param kwargs: Additional keyword arguments
        :return: A redirect to the 'borrower_pending_borrowing' URL
        """
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
    """
    View for displaying pending borrowing records. It checks if user have permission to view pending borrowing records.
    """
    model = Borrowing
    template_name = 'pending_borrowings.html'
    paginate_by = 5
    ordering = ['borrow_date']

    def get_queryset(self):
        """
        Get the queryset based on the request parameters.

        :return: QuerySet: A filtered QuerySet of items with a null return_date.
        """
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
        """
        Get the context data for the function.

        :param kwargs: additional keyword arguments
        :return: the context data including 'order_by' and 'dir'
        """
        context = super().get_context_data(**kwargs)
        context['order_by'] = self.request.GET.get('order_by', 'borrow_date')
        context['dir'] = self.request.GET.get('dir', 'asc')
        return context

class BorrowerPendingBrrowingListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    View for displaying the pending borrowings of a borrower. It checks if the user has permission to access the page.
    """
    model = Borrowing
    template_name = 'borrower_pending_borrowings.html'
    paginate_by = 5
    ordering = ['borrow_date']
    permission_required = ('book_management.can_borrow', 'book_management.can_return')
    raise_exception = False

    def get(self, request, *args, **kwargs):
        """
        Perform a GET request with permission checking. 

        Args:
            request: The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The result of the GET request.
        """
        if not self.has_permission():
            return self.handle_no_permission()

        return super().get(request, *args, **kwargs)

    def handle_no_permission(self):
        """
        Handle the case when the user does not have permission to access the page.

        :param self: The current instance of the class.
        :return: None
        """
        if self.raise_exception:
            return super().handle_no_permission()

        messages.error(self.request, 'You do not have permission to access this page.', extra_tags='bg-danger')
        return self.redirect_to_login()

    def redirect_to_login(self):
        """
        Redirect to the login page.
        No parameters.
        Returns a redirect to the 'login' page.
        """
        return redirect(reverse_lazy('login'))

    def get_queryset(self):
        """
        Return a filtered queryset of borrowed items for the current user.
        """
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
        """
        Get the context data for the view.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The context data.
        """
        context = super().get_context_data(**kwargs)
        context['order_by'] = self.request.GET.get('order_by', 'borrow_date')
        context['dir'] = self.request.GET.get('dir', 'asc')
        return context
    
class BorrowingHistoryView(LibrarianRequiredMixin, ListView):
    """
    View for displaying the history of borrowed books. It checks if the user has permission to access the page.
    """
    model = Borrowing
    template_name = 'borrowing_history.html'
    paginate_by = 5
    ordering = ['borrow_date']

    def get_queryset(self):
        """
        Returns the filtered queryset based on the request parameters.

        Parameters:
            self: The instance of the class.
        
        Returns:
            QuerySet: The filtered queryset based on the request parameters.
        """
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
        """
        Get the context data for the view.

        :param kwargs: keyword arguments
        :return: context data
        """
        context = super().get_context_data(**kwargs)
        context['order_by'] = self.request.GET.get('order_by', 'borrow_date')
        context['dir'] = self.request.GET.get('dir', 'asc')
        return context

class BorrowerBorrowingHistoryView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    View for displaying the history of borrowed books of a borrower. It checks if the user has permission to access the page.
    """
    model = Borrowing
    template_name = 'borrowing_history.html'
    paginate_by = 5
    ordering = ['borrow_date']
    permission_required = ('book_management.can_borrow', 'book_management.can_return')
    raise_exception = False

    def get(self, request, *args, **kwargs):
        """
        Perform a GET request with the given parameters and return the result.
        """
        if not self.has_permission():
            return self.handle_no_permission()

        return super().get(request, *args, **kwargs)

    def handle_no_permission(self):
        """
        Handle the case when the user has no permission to access a page.

        This function does not take any parameters and does not return any value.
        If self.raise_exception is True, it calls the base class's handle_no_permission method.
        Otherwise, it displays an error message and redirects the user to the login page.
        """
        if self.raise_exception:
            return super().handle_no_permission()

        messages.error(self.request, 'You do not have permission to access this page.', extra_tags='bg-danger')
        return self.redirect_to_login()

    def redirect_to_login(self):
        """
        Redirects to the login page.
        """
        return redirect(reverse_lazy('login'))

    def get_queryset(self):
        """
        Return the filtered queryset based on the request parameters.

        Parameters:
            self: The instance of the class.
        
        Returns:
            Queryset: The filtered queryset based on the request parameters.
        """
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
        """
        Return the context data for the view, including any extra context provided by the super class.
        Accepts keyword arguments.
        """
        context = super().get_context_data(**kwargs)
        context['order_by'] = self.request.GET.get('order_by', 'borrow_date')
        context['dir'] = self.request.GET.get('dir', 'asc')
        return context

class BorrowingDetailsView(LoginRequiredMixin, DetailView):
    """
    View for displaying the details of a borrowing. It checks if the user has permission to access the page.
    """
    model = Borrowing
    template_name = 'borrowing_detail.html'
    context_object_name = 'borrowing'

class CustomSignupView(FormView):
    """
    View for signing up a user.
    """
    template_name = 'signup.html'
    form_class = CustomSignupForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        """
        Validate the form and save the user's information. 

        Args:
            form: The form to be validated.

        Returns:
            The result of calling the parent class's form_valid method.
        """
        user = form.save()
        messages.success(self.request, 'Account created successfully.', extra_tags='bg-success')
        return super().form_valid(form)

class CustomLoginView(FormView):
    """
    View for logging in a user.
    """
    template_name = 'login.html'
    form_class = CustomLoginForm
    success_url = reverse_lazy('book_list')

    def form_valid(self, form):
        """
        Method to handle the validation of a form.
        
        Args:
            form: The form to be validated.

        Returns:
            The result of calling the form_valid method of the superclass.
        """
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Logged in successfully.', extra_tags='bg-success')
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        Return the success URL based on the user's permissions and status.
        """
        # Check if the user is a staff user
        if self.request.user.is_staff:
            return reverse_lazy('book_list')
        elif self.request.user.has_perm('book_management.can_borrow') and self.request.user.has_perm('book_management.can_return'):
            return reverse_lazy('available_books')
        else:
            return reverse_lazy('available_books_anonymous') 

class CustomLogoutView(View):
    """
    View for logging out a user.
    """
    
    def get(self, request, *args, **kwargs):
        """
        Perform a GET request, log out the user, display a success message, and redirect to the login page.
        
        :param request: the HTTP request object
        :param args: additional positional arguments
        :param kwargs: additional keyword arguments
        :return: a redirection to the 'login' page
        """
        logout(request)
        messages.success(request, 'Logged out successfully.', extra_tags='bg-success')
        return redirect('login')
