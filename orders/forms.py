from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Folder


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=64, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=1024, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    password1 = forms.CharField(max_length=30, required=True, help_text='Required.')
    password2 = forms.CharField(max_length=30, required=True, help_text='Required.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2' )

class PlaceForm(forms.Form):
    name = forms.CharField(max_length=64, required=True, help_text='*')
    location = forms.CharField(max_length=128, required=True, help_text='*')
    category = forms.ModelChoiceField(queryset=Folder.objects.all(), initial=0)
    un = forms.CharField(max_length=64, required=True, help_text='*')
    pw = forms.CharField(max_length=64, widget=forms.PasswordInput, required=True, help_text='*')

    class Meta:
        model = User
        fields = ('name', 'location', 'category', 'email', 'un', 'pw' )
