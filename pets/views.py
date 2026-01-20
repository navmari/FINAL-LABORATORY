from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from .models import Pet, AdoptionApplication, Shelter
from .forms import AdoptionApplicationForm
from .models import PetCareTip

def pet_detail(request, pk):
    pet = Pet.objects.get(pk=pk)
    return render(request, 'app/pet_detail.html', {'pet': pet})

# Public Home Page - lists all available pets
def home(request):
    pets = Pet.objects.filter(status='AVAILABLE')
    tips = PetCareTip.objects.all()[:5]
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        pets = pets.filter(
            models.Q(species__icontains=search_query) | 
            models.Q(breed__icontains=search_query) |
            models.Q(pet_name__icontains=search_query)
        )
    
    return render(request, 'app/home.html', {'pets': pets, 'tips': tips})


# Role-based redirect after login
@login_required
def role_based_redirect(request):
    profile = request.user.profile

    if profile.role == 'SHELTER':
        return redirect('dashboard')   # Shelter dashboard
    elif profile.role == 'ADOPTER':
        return redirect('home')        # Public adoption UI
    else:
        return redirect('/admin/')


@login_required
def adopt_pet(request, pk):
    pet = Pet.objects.get(pk=pk)

    if request.method == 'POST':
        form = AdoptionApplicationForm(request.POST)
        if form.is_valid():
            profile = request.user.profile
            application = form.save(commit=False)
            application.pet = pet
            application.first_name = profile.name or request.user.username
            application.middle_name = ''
            application.last_name = ''
            application.email = request.user.email or ''
            application.pet_name = pet.pet_name
            application.pet_image = (pet.pet_image.name if pet.pet_image else '')
            application.status = AdoptionApplication.PENDING
            application.save()

            # Send notification to shelter (development: printed to console)
            if pet.shelter and pet.shelter.email:
                subject = f"New Adoption Application for {pet.pet_name}"
                message = (
                    f"A new adoption application (ID: {application.pk}) was submitted for {pet.pet_name}.\n\n"
                    f"Applicant: {application.first_name}\n"
                    f"Email: {application.email}\n"
                    f"Phone: {application.phone_number}\n\n"
                    f"Reason:\n{application.reason_for_adoption}\n\n"
                    f"Manage applications in the shelter dashboard."
                )
                try:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [pet.shelter.email], fail_silently=True)
                except Exception:
                    # fail silently in dev
                    pass

            from django.contrib import messages
            messages.success(request, f'Adoption application for {pet.pet_name} submitted.')
            return redirect('application-detail', pk=application.pk)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial['address'] = ''
        form = AdoptionApplicationForm(initial=initial)

    return render(request, 'app/adopt_form.html', {'pet': pet, 'form': form})


@login_required
def application_detail(request, pk):
    application = AdoptionApplication.objects.get(pk=pk)
    # Only the applicant or shelter staff should view; basic protection: allow owner or shelter staff
    is_owner = (request.user.email and request.user.email == application.email) or (request.user.profile.name == application.first_name)
    is_shelter = hasattr(request.user, 'profile') and request.user.profile.role == 'SHELTER'
    if not (is_owner or is_shelter):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden('Not authorized to view this application')

    return render(request, 'app/application_detail.html', {'application': application})


def pet_tips(request):
    tips = PetCareTip.objects.all()
    return render(request, 'app/pet_tips.html', {'tips': tips})


def pet_tip_detail(request, pk):
    """Display the full detail of a single pet care tip."""
    tip = PetCareTip.objects.get(pk=pk)
    return render(request, 'app/pet_tip_detail.html', {'tip': tip})


@login_required
def my_applications(request):
    """Display all adoption applications for the logged-in adopter."""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Filter applications by the current user's email
    applications = AdoptionApplication.objects.filter(
        email=request.user.email
    ).select_related('pet', 'pet__shelter').order_by('-created_at')
    
    # Status-based messaging for each application
    status_messages = {
        AdoptionApplication.PENDING: {
            'label': 'Pending Review',
            'message': 'Your application is being reviewed by the shelter. You will be notified of the decision soon.',
            'badge_class': 'badge-pending'
        },
        AdoptionApplication.APPROVED: {
            'label': 'Approved',
            'message': 'Congratulations! Your application has been approved. Please contact the shelter to finalize the adoption.',
            'badge_class': 'badge-approved',
            'action': 'Contact Shelter'
        },
        AdoptionApplication.REJECTED: {
            'label': 'Not Approved',
            'message': 'Unfortunately, your application was not approved. Please explore other pets available for adoption.',
            'badge_class': 'badge-rejected',
            'action': 'Browse Pets'
        },
        AdoptionApplication.COMPLETED: {
            'label': 'Completed',
            'message': 'Adoption completed! We hope you and your pet have a wonderful life together.',
            'badge_class': 'badge-completed'
        }
    }
    
    # Add status messages to each application
    for app in applications:
        if app.status in status_messages:
            app.status_info = status_messages[app.status]
        else:
            app.status_info = {'label': app.get_status_display(), 'message': '', 'badge_class': 'badge-default'}
    
    return render(request, 'app/my_applications.html', {'applications': applications})


def about(request):
    """Display About PetConnect page with shelters list"""
    shelters = Shelter.objects.all()
    return render(request, 'app/about.html', {'shelters': shelters})
