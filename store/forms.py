from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(forms.Form):
    """
    Form for new user registration with username, email, password, and confirmation.
    """
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Choose a username',
            'class': 'form-input',
            'autocomplete': 'username',
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'class': 'form-input',
            'autocomplete': 'email',
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create a strong password',
            'class': 'form-input',
            'autocomplete': 'new-password',
        })
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Re-enter your password',
            'class': 'form-input',
            'autocomplete': 'new-password',
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match. Please verify and try again.")

        return cleaned_data


class UserLoginForm(forms.Form):
    """
    Form for user login credentials.
    """
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Your username',
            'class': 'form-input',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Your password',
            'class': 'form-input',
            'autocomplete': 'current-password',
        })
    )


class CheckoutForm(forms.Form):
    """
    Form for collecting customer shipping and contact details at checkout.
    """
    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. John Doe',
            'class': 'form-input',
            'autocomplete': 'name',
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'e.g. john@example.com',
            'class': 'form-input',
            'autocomplete': 'email',
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. +1 555-123-4567',
            'class': 'form-input',
            'autocomplete': 'tel',
        })
    )
    address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'placeholder': 'Street address, apartment, city, state, postal code',
            'class': 'form-input',
            'rows': 3,
            'autocomplete': 'street-address',
        })
    )
