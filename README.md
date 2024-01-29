# Library Management System

The Library Management System is a Django-based web application designed for managing books, borrowers, and borrowing activities in a library.

## Features

- **Books Management:** Add, update, and delete books, including details such as title, author, ISBN, publication date, and availability status.
- **Borrowers Management:** Create, update, and delete borrower profiles, including basic information like name and phone number.
- **Borrowing System:** Track borrowing activities, including borrow and return dates, for efficient library management.
- **User Authentication:** Users can sign up, log in, and log out securely. Librarians are restricted from being borrowers.
- **Permissions:** Define permissions for users, such as the ability to borrow or return books.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/wdcs-pruthvithakor/library_management.git
    cd library_management
    ```

2. Create a virtual environment and install dependencies:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'
    pip install -r requirements.txt
    ```

3. Configure the environment variables:

    Create a `.env` file in the project root and set the necessary environment variables:

    ```env
    POSTGREDB_NAME='library_management'
    POSTGREDB_USER='postgres'
    POSTGREDB_PASSWORD='postgres'
    POSTGREDB_HOST='127.0.0.1'
    POSTGREDB_PORT='5432'
    ```

4. Run migrations:

    ```bash
    python manage.py migrate
    ```

5. Create a superuser account:

    ```bash
    python manage.py createsuperuser
    ```

6. Run the development server:

    ```bash
    python manage.py runserver
    ```

Visit [http://localhost:8000/](http://localhost:8000/) to access the application. Admin panel is available at [http://localhost:8000/admin/](http://localhost:8000/admin/).

## Type of Users & Permissions

1. **Superuser:** Has full access to the application.
2. **User:** Can only view available books. ( Ask admin to add as librarian or borrower. )
3. **Librarian:** Can view, edit, create, and delete books and borrowers. Can view pending borrowed books and borrowing history of all users.
4. **Borrwers:** Can view, borrow, and return available books. Can view their borrowing history and pending borrowed books.

## Usage

1. Log in using the created superuser account on [http://localhost:8000/admin/](http://localhost:8000/admin/).
2. Make staff accounts for librarians.
3. Log in on the [http://localhost:8000/](http://localhost:8000/) with the created user account.
4. Add Borrowers and Books. You can check borrowing history and pending borrowed books of all borrowers.
5. Log in using borrower account to borrow and return books.
6. Borrower can check their borrowing history and pending borrowed books.
7. If you Log in with user which is not borrower or librarian, you will be redirected to available book list page where you can only view details of books.

## URLs

- `/login/`: Log in to the system.
- `/logout/`: Log out of the system.
- `/signup/`: Sign up for a new user account.
- `/borrowers/`: View the list of borrowers.
- `/borrower/create/`: Create a new borrower profile.
- `/books/`: View the list of books.
- `/book/create/`: Create a new book entry.
- `/available/`: View available books.
- `/borrow/`: Borrow a book.
- `/return/`: Return a borrowed book.
- `/pending/`: View pending borrowings.
- `/history/`: View borrowing history.
- `/borrower/history/`: View borrower-specific borrowing history.

Certainly! Here's an extended README.md section for testing your Django project:

## Testing

The project uses the Django testing framework for writing and running tests. Before running tests, ensure you have set up the project and activated the virtual environment.

### Running Tests

To run the tests, use the following command:

```bash
python manage.py test
```

This will discover and run all the tests in the `tests` directory.

### Writing Tests

Tests are organized in the `tests` directory. Django's test classes and methods are utilized to cover various aspects of the application, including models, views, forms, and functionalities.

#### Example Test Structure

```python
# Example test file: tests/test_models.py

from django.test import TestCase
from .models import Book, Borrower, Borrowing

class BookModelTest(TestCase):
    def test_has_pending_returns(self):
        # Test the has_pending_returns method for the Book model
        # ...

class BorrowerModelTest(TestCase):
    def test_has_pending_returns(self):
        # Test the has_pending_returns method for the Borrower model
        # ...

class BorrowingModelTest(TestCase):
    def test_borrowing_dates(self):
        # Test the borrow and return dates for the Borrowing model
        # ...
```

### Test Coverage

While writing tests, aim to achieve high test coverage to ensure the reliability of the application. Use tools like coverage.py to measure code coverage:

1. Install coverage.py:

    ```bash
    pip install coverage
    ```

2. Run tests with coverage:

    ```bash
    coverage run manage.py test
    ```

3. Generate coverage report:

    ```bash
    coverage report -m
    ```

This will display a detailed report indicating the percentage of code coverage.

### Mocking and Fixtures

Use Django's `TestCase` class to create fixtures and mock objects for testing. This ensures that tests are isolated and do not interfere with each other.

### Continuous Integration (CI)

Check Continous Integration pipeline of this project. This ensures that tests are automatically run whenever changes are pushed to the repository, helping to catch and address issues early in the development process.