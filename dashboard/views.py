# dashboard/views.py
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import redirect
from pets.models import Pet, AdoptionApplication
from pets.models import Shelter
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse

# Shelter role check
def shelter_check(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'SHELTER'

# Dashboard home
@method_decorator([login_required, user_passes_test(shelter_check)], name='dispatch')
class DashboardHomeView(TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shelter = self.request.user.profile.shelter
        pets = Pet.objects.filter(shelter=shelter)
        context['pets'] = pets
        context['pets_count'] = pets.count()
        context['pending_apps_count'] = AdoptionApplication.objects.filter(
            pet__shelter=shelter,
            status=AdoptionApplication.PENDING
        ).count()
        # include pending applications for quick actions on the dashboard
        context['pending_applications'] = AdoptionApplication.objects.filter(
            pet__shelter=shelter,
            status=AdoptionApplication.PENDING
        ).select_related('pet')[:10]
        return context


@method_decorator([login_required, user_passes_test(shelter_check)], name='dispatch')
class RequestShelterView(TemplateView):
    template_name = 'dashboard/request_shelter.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # show available shelters for user to reference when contacting admin
        context['shelters'] = Shelter.objects.all()
        return context

# Pet views
@method_decorator([login_required, user_passes_test(shelter_check)], name='dispatch')
class PetListView(ListView):
    model = Pet
    template_name = 'dashboard/pet_list.html'
    context_object_name = 'pets'

    def get_queryset(self):
        return Pet.objects.filter(shelter=self.request.user.profile.shelter)

@method_decorator([login_required, user_passes_test(shelter_check)], name='dispatch')
class PetCreateView(CreateView):
    model = Pet
    # Exclude `shelter` to ensure the server assigns it from the logged-in user's profile
    fields = [
        'pet_name', 'species', 'breed', 'gender', 'age_years', 'age_months',
        'health_status', 'description', 'status', 'adoption_fee', 'pet_image'
    ]
    template_name = 'dashboard/pet_form.html'
    success_url = reverse_lazy('dashboard-pets')

    def form_valid(self, form):
        shelter = getattr(self.request.user.profile, 'shelter', None)
        if not shelter:
            messages.error(self.request, 'Your account is not associated with a shelter. Contact an administrator.')
            return redirect('dashboard')
        form.instance.shelter = shelter
        return super().form_valid(form)

@method_decorator([login_required, user_passes_test(shelter_check)], name='dispatch')
class PetUpdateView(UpdateView):
    model = Pet
    # Disallow editing the `shelter` relationship from the dashboard
    fields = [
        'pet_name', 'species', 'breed', 'gender', 'age_years', 'age_months',
        'health_status', 'description', 'status', 'adoption_fee', 'pet_image'
    ]
    template_name = 'dashboard/pet_form.html'
    success_url = reverse_lazy('dashboard-pets')

    def get_queryset(self):
        return Pet.objects.filter(shelter=self.request.user.profile.shelter)

@method_decorator([login_required, user_passes_test(shelter_check)], name='dispatch')
class PetDeleteView(DeleteView):
    model = Pet
    template_name = 'dashboard/pet_confirm_delete.html'
    success_url = reverse_lazy('dashboard-pets')

    def get_queryset(self):
        return Pet.objects.filter(shelter=self.request.user.profile.shelter)

# Adoption applications
@method_decorator([login_required, user_passes_test(shelter_check)], name='dispatch')
class AdoptionApplicationListView(ListView):
    model = AdoptionApplication
    template_name = 'dashboard/adoption_list.html'
    context_object_name = 'applications'

    def get_queryset(self):
        return AdoptionApplication.objects.filter(
            pet__shelter=self.request.user.profile.shelter
        ).select_related('pet')

@login_required
@user_passes_test(shelter_check)
def update_application_status(request, pk, status):
    # only allow POST to change status
    if request.method != 'POST':
        return redirect('dashboard-adoptions')

    application = AdoptionApplication.objects.get(
        pk=pk,
        pet__shelter=request.user.profile.shelter
    )
    application.status = status
    application.save()
    
    # If application is approved, mark pet as ADOPTED
    if status == 'APPROVED':
        application.pet.status = 'ADOPTED'
        application.pet.save()
    
    # send notification to applicant
    try:
        subject = f"Adoption application {application.request_id} update"
        message = (
            f"Hello {application.first_name},\n\n"
            f"Your adoption application for {application.pet.pet_name} (ID {application.request_id}) has been set to: {application.status}.\n\n"
            "If you have questions, please contact the shelter.\n\n"
            "Thanks,\nPetConnect Team"
        )
        send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@petconnect.local'), [application.email], fail_silently=True)
    except Exception:
        pass
    messages.success(request, f'Application {application.request_id} set to {status}.')
    return redirect('dashboard-adoptions')


@login_required
@user_passes_test(shelter_check)
def adoption_application_detail(request, pk):
    application = AdoptionApplication.objects.get(
        pk=pk,
        pet__shelter=request.user.profile.shelter
    )
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            application.status = AdoptionApplication.APPROVED
            # notify applicant
            try:
                subject = f"Adoption application {application.request_id} approved"
                message = (
                    f"Hello {application.first_name},\n\n"
                    f"Good news — your adoption application for {application.pet.pet_name} (ID {application.request_id}) has been approved.\n\n"
                    "The shelter will contact you with next steps.\n\n"
                    "Thanks,\nPetConnect Team"
                )
                send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@petconnect.local'), [application.email], fail_silently=True)
            except Exception:
                pass
            messages.success(request, 'Application approved.')
        elif action == 'reject':
            application.status = AdoptionApplication.REJECTED
            # notify applicant
            try:
                subject = f"Adoption application {application.request_id} update"
                message = (
                    f"Hello {application.first_name},\n\n"
                    f"We are sorry to inform you that your adoption application for {application.pet.pet_name} (ID {application.request_id}) has been rejected.\n\n"
                    "If you have questions, please contact the shelter.\n\n"
                    "Thanks,\nPetConnect Team"
                )
                send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@petconnect.local'), [application.email], fail_silently=True)
            except Exception:
                pass
            messages.success(request, 'Application rejected.')
        application.save()
        return redirect('dashboard-adoptions')

    return render(request, 'dashboard/adoption_detail.html', {'application': application})


@login_required
@user_passes_test(shelter_check)
def pet_detail(request, pk):
    # show pet info to shelter staff for their shelter
    pet = get_object_or_404(Pet, pk=pk, shelter=request.user.profile.shelter)
    # include related applications
    applications = pet.applications.all()
    return render(request, 'dashboard/pet_detail.html', {'pet': pet, 'applications': applications})


@login_required
@user_passes_test(shelter_check)
def approve_all_applications(request, pk):
    if request.method != 'POST':
        return redirect('dashboard-pet-detail', pk=pk)

    pet = get_object_or_404(Pet, pk=pk, shelter=request.user.profile.shelter)
    pending = pet.applications.filter(status=AdoptionApplication.PENDING)
    count = 0
    for app in pending:
        app.status = AdoptionApplication.APPROVED
        app.save()
        count += 1
        # notify each applicant
        try:
            subject = f"Adoption application {app.request_id} approved"
            message = (
                f"Hello {app.first_name},\n\n"
                f"Good news — your adoption application for {app.pet.pet_name} (ID {app.request_id}) has been approved.\n\n"
                "The shelter will contact you with next steps.\n\n"
                "Thanks,\nPetConnect Team"
            )
            send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@petconnect.local'), [app.email], fail_silently=True)
        except Exception:
            pass
    messages.success(request, f'Approved {count} application(s) for {pet.pet_name}.')
    return redirect('dashboard-pet-detail', pk=pk)
