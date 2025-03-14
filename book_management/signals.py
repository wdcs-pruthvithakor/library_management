"""
Signals for library_management application.
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission, User
from .models import Borrower

@receiver(post_save, sender=Borrower)
def add_borrower_permissions(sender, instance, **kwargs):
    """
    Triggered after a Borrower instance is saved. Adds borrower permissions to the associated user if the borrower instance is created.
    
    Args:
        sender: The sender of the signal.
        instance: The instance of the saved Borrower.
        **kwargs: Arbitrary keyword arguments.
    """
    if kwargs['created']:
        borrower_user = instance.user
        borrower_user.user_permissions.add(
            Permission.objects.get(codename='can_borrow'),
            Permission.objects.get(codename='can_return'),
        )

@receiver(post_delete, sender=Borrower)
def remove_borrower_permissions(sender, instance, **kwargs):
    """
    Remove borrower permissions when a Borrower instance is deleted.
    Args:
        sender: The sender of the signal.
        instance: The instance being deleted.
        **kwargs: Additional keyword arguments.
    Returns:
        None
    """
    borrower_user = instance.user
    borrower_user.user_permissions.remove(
        Permission.objects.get(codename='can_borrow'),
        Permission.objects.get(codename='can_return'),
    )

@receiver(pre_save, sender=Borrower)
def update_borrower_permissions(sender, instance, **kwargs):
    """
    Update borrower permissions before saving the instance.

    Args:
        sender: The sender of the signal.
        instance: The instance being saved.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """
    if instance.pk:
        # If the instance has a primary key, it means it's being updated
        old_borrower = Borrower.objects.get(pk=instance.pk)
        old_user = old_borrower.user

        # Remove permissions from the old user
        old_user.user_permissions.remove(
            Permission.objects.get(codename='can_borrow'),
            Permission.objects.get(codename='can_return'),
        )

        # Add permissions to the new user
        new_user = instance.user
        new_user.user_permissions.add(
            Permission.objects.get(codename='can_borrow'),
            Permission.objects.get(codename='can_return'),
        )
