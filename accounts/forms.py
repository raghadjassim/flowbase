from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignupForm(UserCreationForm):
    first_name = forms.CharField(label="Full name", max_length=60)
    email = forms.EmailField(label="Email")

    class Meta:
        model = User
        fields = ["first_name", "username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "first_name": "e.g. Jane Smith",
            "username": "Username",
            "email": "you@company.com",
            "password1": "Password",
            "password2": "Confirm password",
        }
        for name, field in self.fields.items():
            field.widget.attrs.update({"placeholder": placeholders.get(name, ""), "class": "fb-input"})


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={"class": "fb-input", "placeholder": "Username"}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"class": "fb-input", "placeholder": "••••••••"}))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "job_title", "bio", "email", "email_reminders"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "fb-input"}),
            "last_name": forms.TextInput(attrs={"class": "fb-input"}),
            "job_title": forms.TextInput(attrs={"class": "fb-input", "placeholder": "e.g. Frontend Developer"}),
            "bio": forms.TextInput(attrs={"class": "fb-input", "placeholder": "A short bio about you"}),
            "email": forms.EmailInput(attrs={"class": "fb-input"}),
        }
