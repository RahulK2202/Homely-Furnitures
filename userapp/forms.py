from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import *
from django.contrib.auth.forms import UserChangeForm



class CreateUserForm(UserCreationForm):
    class Meta:
        model = Customer
        fields = ['username', 'email','password1', 'password2']


from django import forms
from django.contrib.auth.forms import UserChangeForm


class UpdateUserForm(UserChangeForm):
    first_name = forms.CharField(max_length=50, required=True )
    last_name = forms.CharField(max_length=50, required=True)
    phone = forms.CharField(max_length=15, required=True)
    address_line_1 = forms.CharField(max_length=50, required=True)
    address_line_2 = forms.CharField(max_length=50, required=True)
    city = forms.CharField(max_length=50, required=True)
    state = forms.CharField(max_length=50, required=True)
    pincode = forms.CharField(max_length=10, required=True)

    class Meta:
        model = Customer
        fields = ['phone', 'first_name', 'profile_pic','last_name', 'address_line_1', 'address_line_2','city', 'state', 'pincode']

