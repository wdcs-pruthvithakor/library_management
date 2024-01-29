
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from .validators import CustomPasswordValidator
from .models import Book, Borrower

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'

class BorrowerForm(forms.ModelForm):
    class Meta:
        model = Borrower
        fields = '__all__'
    
    def clean_user(self):
        user = self.cleaned_data.get('user')

        if user.is_staff:
            raise ValidationError("Librarians are not allowed to be borrowers.")

        return user


class CustomSignupForm(forms.Form):
    username = forms.CharField(max_length=150, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')
    password = forms.CharField(widget=forms.PasswordInput,help_text=CustomPasswordValidator().get_help_text())
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    confirm_password = forms.CharField(widget=forms.PasswordInput, help_text='Enter the same password as before, for verification.')

    def clean_username(self):
        username = self.cleaned_data['username']
        
        # Adding custom validation for username
        if len(username) > 150:
            raise forms.ValidationError('Username must be 150 characters or fewer.')
        if not username.isalnum() and '@' not in username and '.' not in username and '+' not in username and '-' not in username and '_' not in username:
            raise forms.ValidationError('Username can only contain letters, digits, and @/./+/-/_ characters.')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already in use.')

        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "The two password fields didn't match.")

        # Use custom password validation
        custom_password_validator = CustomPasswordValidator()
        try:
            custom_password_validator.validate(password)
        except ValidationError as error:
            self.add_error('password', error)

    def save(self, commit=False):
        password = make_password(self.cleaned_data['password'])
        email = self.cleaned_data['email']
        user = User.objects.create(username=self.cleaned_data['username'], password=password, email=email)
        return user
    
    def get_help_text(self):
        return CustomPasswordValidator().get_help_text()


class CustomLoginForm(forms.Form):
    username = forms.CharField(max_length=150, help_text='Enter your username')
    password = forms.CharField(widget=forms.PasswordInput, help_text='Enter your password')


    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = User.objects.filter(username=username).exists()
        if not user:
            self.add_error('username', "Invalid username.")
            return cleaned_data

        user = authenticate(username=username, password=password)
        
        if user is None:
            self.add_error('password', "Authentication failed. Invalid password.")

        return cleaned_data

    def save(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        # Authenticate user
        user = authenticate(username=username, password=password)

        if user is None:
            raise forms.ValidationError("Invalid username or password.")

        return user
