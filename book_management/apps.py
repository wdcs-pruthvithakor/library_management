"""
Apps for library_management application.
"""
from django.apps import AppConfig


class BookManagementConfig(AppConfig):
    """
    BookManagementConfig class.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'book_management'

    def ready(self):
        """
        Method to perform the specified action when the instance is ready.
        No parameters and return type.
        """
        import book_management.signals
