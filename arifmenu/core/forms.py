from django import forms
from django.contrib.auth.models import User
from .models import MenuItem, Place


class SignupForm(forms.ModelForm):
    password = forms.CharField(
        min_length=6, label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "At least 6 characters", "autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("username", "email")
        labels = {"username": "Choose a username", "email": "Email (optional)"}
        help_texts = {"username": ""}
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "e.g. abebe_cafe (no spaces)", "autofocus": True}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class PlaceCreateForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ["name", "place_type", "area", "phone"]
        labels = {"name": "Name of your place", "place_type": "What is it?", "area": "Area / neighborhood", "phone": "Phone (optional)"}
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Abebe Café", "autofocus": True}),
            "area": forms.TextInput(attrs={"placeholder": "e.g. Bole"}),
            "phone": forms.TextInput(attrs={"placeholder": "09..."}),
        }


class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ["name", "place_type", "description", "area", "address", "phone", "opening_hours", "latitude", "longitude", "cover"]


class ItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ["name", "category", "price", "description", "photo", "is_available"]
