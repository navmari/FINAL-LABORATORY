from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from pets.models import UserProfile
from .forms import SignupForm
from .forms import AdminShelterSignupForm
from django.contrib.auth.decorators import user_passes_test

# Signup view
def signup(request):
    next_url = request.GET.get('next', None)  # preserve next parameter

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()

            # `SignupForm.save()` already creates the UserProfile with `name` and `role`.

            # Automatically log in
            authenticated_user = authenticate(
                request, username=user.username, password=request.POST['password1']
            )
            if authenticated_user:
                login(request, authenticated_user)
                return redirect(next_url or 'home')
    else:
        form = SignupForm()

    return render(request, 'registration/signup.html', {'form': form, 'next': next_url})


# Login view using built-in form
def custom_login(request):
    next_url = request.GET.get('next', None)

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Redirect based on role
            if user.profile.role == 'SHELTER':
                return redirect('dashboard')
            return redirect(next_url or 'home')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form, 'next': next_url})


def is_superuser(user):
    return user.is_authenticated and user.is_superuser


@user_passes_test(is_superuser)
def admin_create_shelter(request):
    if request.method == 'POST':
        form = AdminShelterSignupForm(request.POST)
        if form.is_valid():
            form.save()
            from django.contrib import messages
            messages.success(request, 'Shelter account created successfully.')
            return redirect('admin:index')
    else:
        form = AdminShelterSignupForm()

    return render(request, 'registration/admin_shelter_signup.html', {'form': form})
