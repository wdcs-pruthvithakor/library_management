"""
Validators for library_management application.
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re

class CustomPasswordValidator:
    def __init__(self, min_length=8, requires_digit=True, requires_uppercase=True):
        self.min_length = min_length
        self.requires_digit = requires_digit
        self.requires_uppercase = requires_uppercase

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("The password must be at least {0} characters long.").format(self.min_length),
                code='password_too_short',
            )

        if self.requires_digit and not re.search(r'\d', password):
            raise ValidationError(
                _("The password must contain at least one digit."),
                code='password_no_digit',
            )

        if self.requires_uppercase and not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("The password must contain at least one uppercase letter."),
                code='password_no_uppercase',
            )

    def get_help_text(self):
        return _(
            "Your password must be at least {0} characters long. <br/> "
            "Your password must contain at least one digit. <br>"
            "Your password must contain at least one uppercase letter."
        ).format(self.min_length)
