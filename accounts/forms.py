from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from pets.models import UserProfile
from pets.models import Shelter


class SignupForm(UserCreationForm):
    name = forms.CharField(max_length=200, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                name=self.cleaned_data.get('name'),
                role='ADOPTER'
            )
        return user


class AdminShelterSignupForm(UserCreationForm):
    name = forms.CharField(max_length=200, required=True)
    email = forms.EmailField(required=True)
    shelter = forms.ModelChoiceField(queryset=Shelter.objects.all(), required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'name', 'shelter']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
            profile = UserProfile.objects.create(
                user=user,
                name=self.cleaned_data.get('name'),
                role='SHELTER'
            )
            profile.shelter = self.cleaned_data.get('shelter')
            profile.save()
        return user
