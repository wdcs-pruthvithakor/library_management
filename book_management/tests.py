"""
Tests for library_management application.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Book, Borrower, Borrowing

class LibraryAuthTests(TestCase):
    def setUp(self):
        """
        Set up the test environment by creating instances of Book, User, and Borrower for testing purposes.
        """
        self.book = Book.objects.create(title='Test Book', author='Test Author', ISBN='1234567890', publication_date='2022-01-01', availability_status=True)
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.borrower = Borrower.objects.create(name='Test Borrower', user=self.user, phone_number='1234567890')

    def test_sign_up_view(self):
        """
        Test the sign up view by sending a POST request with user data and checking for the expected response and database entry.
        """
        url = reverse('signup')
        data = {'username': 'newuser', 'email':'newuser@example.com','password': 'Userpass001', 'confirm_password': 'Userpass001'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful signup
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view(self):
        """
        Test the login view by creating a test user, logging in, and checking the response.
        """
        # Create a test user
        user = User.objects.create_user(username='testuser1', password='Userpass001', email='testuser@example.com')

        # Log in the user
        url = reverse('login')
        data = {'username': 'testuser1', 'password': 'Userpass001'}
        response = self.client.post(url, data, follow=True)
        self.assertQuerySetEqual(response.context['object_list'], [self.book])
        self.assertContains(response, 'Test Author')
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        """
        Test the logout view by creating a test user, logging in, and then logging out. 
        Check if the logout redirects and if the user session is cleared.
        """
        # Create a test user
        user = User.objects.create_user(username='testuser1', password='Userpass001', email='testuser@example.com')

        # Log in the user
        self.client.login(username='testuser', password='testpass')

        # Log out the user
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after successful logout
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
class BorrowerViewTests(TestCase):
    def setUp(self):
        """
        Set up the necessary objects for the test, including a book, user, client login, and borrower.
        """
        self.book = Book.objects.create(title='Test Book', author='Test Author', ISBN='1234567890', publication_date='2022-01-01', availability_status=True)
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.borrower = Borrower.objects.create(name='Test Borrower', user=self.user, phone_number='1234567890')

    def borrow_book(self, id, username):
        """
        Function to borrow a book.

        :param id: The ID of the book to borrow
        :param username: The username of the borrower
        :return: A tuple containing the HTTP response, the borrowed book, and the borrowing information
        """
        url = reverse('borrow_book')
        data = {'book_id': id, 'username': username}
        response = self.client.post(url, data, follow=True)
        borrowing = Borrowing.objects.get(book=self.book, borrower=self.borrower)
        book = Book.objects.get(id=id)
        return response, book, borrowing
    
    def return_book(self, borrowing_id):
        """
        Returns a response and the borrowing object after returning a book.

        Args:
            self: the instance of the class
            borrowing_id: the ID of the borrowing record

        Returns:
            response: the HTTP response
            borrowing: the borrowing object
        """
        url = reverse('return_book')
        data = {'borrowing_id': borrowing_id}
        response = self.client.post(url, data, follow=True)
        borrowing = Borrowing.objects.get(id=borrowing_id)
        return response, borrowing

    def test_borrow_view(self):
        """
        Function to test the borrow view. 
        """
        response, book, borrowing = self.borrow_book(self.book.id, self.borrower.user.username)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(book.availability_status, False)
        self.assertEqual(borrowing.return_date, None)

    
    def test_return_view(self):
        """
        This function tests the return view by borrowing a book, checking its availability status, returning the book, and then checking the availability status again.
        """
        response, book, borrowing = self.borrow_book(self.book.id, self.borrower.user.username)
        self.assertEqual(book.availability_status, False)
        response, borrowing = self.return_book(borrowing.id)
        book = Book.objects.get(id=self.book.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(book.availability_status, True)

    def test_available_books_view(self):
        """
        Test the available_books view.

        This function sends a GET request to the 'available_books' URL and asserts that the response status code is 200. It also asserts that the response contains the string 'Test Author'.

        Parameters:
        - self: The instance of the test case.

        Returns:
        - None
        """
        url = reverse('available_books')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Author')
        
    def test_pending_borrowed_books(self):
        """
        Test the pending borrowed books function by borrowing a book and checking the response.
        """
        self.borrow_book(self.book.id, self.borrower.user.username)
        url = reverse('borrower_pending_borrowing')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Author')
        
    def test_borrowing_history(self):
        """
        Test the borrowing history functionality by borrowing a book, returning it, and checking the borrowing history.
        """
        response, book, borrowing = self.borrow_book(self.book.id, self.borrower.user.username)
        self.assertEqual(book.availability_status, False)
        response, borrowing = self.return_book(borrowing.id)
        url = reverse('borrower_borrowing_history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'History of Borrowed Books')
        self.assertContains(response, 'Test Book')
        
class LibrarianViewTests(TestCase):
    def setUp(self):
        """
        Set up the necessary objects for the test. Create a book, users, admin user, and borrower for testing.
        """
        self.book = Book.objects.create(title='Test Book', author='Test Author', ISBN='1234567890', publication_date='2022-01-01', availability_status=True)
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass2')
        self.admin_user = User.objects.create_user(username='adminuser', password='adminpass', is_staff=True)
        self.client.login(username='adminuser', password='adminpass')
        self.borrower = Borrower.objects.create(name='Test Borrower', user=self.user, phone_number='1234567890')
    
    def borrow_book(self, id):
        """
        Function to borrow a book using the specified id, and return the response, book, and borrowing details.
        """
        self.client.login(username='testuser', password='testpass')
        url = reverse('borrow_book')
        data = {'book_id': id, 'username': 'testuser'}
        response = self.client.post(url, data, follow=True)
        borrowing = Borrowing.objects.get(book=self.book, borrower=self.borrower)
        book = Book.objects.get(id=id)
        self.client.login(username='adminuser', password='adminpass')
        return response, book, borrowing
    
    def return_book(self, borrowing_id):
        """
        Return a book that was previously borrowed.

        Args:
            self: The object itself.
            borrowing_id (int): The ID of the borrowing record.

        Returns:
            tuple: A tuple containing the HTTP response and the Borrowing object.
        """
        self.client.login(username='testuser', password='testpass')
        url = reverse('return_book')
        data = {'borrowing_id': borrowing_id}
        response = self.client.post(url, data, follow=True)
        borrowing = Borrowing.objects.get(id=borrowing_id)
        self.client.login(username='adminuser', password='adminpass')
        return response, borrowing
        
    def test_book_view(self):
        """
        Test the book view by making a GET request to the 'book_list' URL and 
        asserting the response status code, as well as the presence of certain 
        content in the response.
        """
        url = reverse('book_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Book')
        self.assertContains(response, 'Book List')
        self.assertContains(response, 'Available')
        
    def test_book_create_view(self):
        """
        Test the book create view by posting data and checking the response status code and content.
        """
        url = reverse('book_create')
        data = {'title': 'Test Book1', 'author': 'Test Author1', 'ISBN': '1234567891', 'publication_date': '2022-01-02', 'availability_status': True}
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Book1')
        self.assertContains(response, 'Test Author1')
        
    def test_book_update_view(self):
        """
        Test the book update view by sending a POST request with updated book data and 
        verifying the response status code and content.
        """
        url = reverse('book_update', args=[self.book.id])
        data = {'title': 'Test Book updated', 'author': 'Test Author1', 'ISBN': '1234567892', 'publication_date': '2022-01-02', 'availability_status': False}
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Book updated')
        self.assertContains(response, 'Test Author1')
        self.assertContains(response, 'Not Available')
        
    def test_book_delete_view(self):
        """
        Test the book delete view by sending a POST request and checking the response.
        """
        url = reverse('book_delete', args=[self.book.id])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Test Book')
        
    def test_borrower_view(self):
        """
        Test the borrower view by checking if the expected content is present in the response.
        """
        url = reverse('borrower_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Borrower')
        self.assertContains(response, 'Borrower List')
        self.assertContains(response, '1234567890')
        
    def test_borrower_create_view(self):
        """
        Test the borrower create view by sending a POST request with test data and 
        checking the response status code and content.
        """
        url = reverse('borrower_create')
        data = {'name': 'Test Borrower1', 'phone_number': '1234567891', 'user': self.user2.id}
        respose = self.client.post(url, data, follow=True)
        self.assertEqual(respose.status_code, 200)
        self.assertContains(respose, 'Test Borrower1')
        self.assertContains(respose, '1234567891')
        
    def test_borrower_update_view(self):
        """
        Test the borrower update view by posting data and checking the response.
        """
        url = reverse('borrower_update', args=[self.borrower.id])
        data = {'name': 'Test Borrower updated', 'phone_number': '1234567892', 'user': self.user2.id}
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Borrower updated')
        self.assertContains(response, '1234567892')
 
    def test_borrower_delete_view(self):
        """
        Test the borrower delete view by sending a post request and checking the response status code and content.
        """
        url = reverse('borrower_delete', args=[self.borrower.id])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Test Borrower')
        
    def test_pending_borrowing_view(self):
        """
        Test the pending borrowing view by borrowing a book, accessing the pending borrowing URL,
        and checking the response for the expected content.
        """
        self.borrow_book(self.book.id)
        url = reverse('pending_borrowing')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Book')
        self.assertContains(response, 'Test Borrower')
        self.assertContains(response, 'Pending Borrowed Books')
        
    def test_borrowing_history_view(self):
        """
        Test the borrowing history view by performing a series of book borrowing and returning actions, and then checking the response and content for specific details.
        """
        response, book, borrowing = self.borrow_book(self.book.id)
        self.assertEqual(book.availability_status, False)
        response, borrowing = self.return_book(borrowing.id)
        url = reverse('borrowing_history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'History of Borrowed Books')
        self.assertContains(response, 'Test Book')
        self.assertContains(response, 'Test Borrower')
