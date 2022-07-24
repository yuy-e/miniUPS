import imp
from django import forms
from django.forms import ModelForm
from pyrsistent import field
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UpsUpdate(forms.Form):
    location_x = forms.CharField(label='Location_x')
    location_y = forms.CharField(label='Location_y')


class FindPackage(forms.Form):
    tracking_num = forms.IntegerField(label='Input tracking number')
