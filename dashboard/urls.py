# dashboard/urls.py
from django.urls import path
from .views import (
    DashboardHomeView,
    PetListView,
    PetCreateView,
    PetUpdateView,
    PetDeleteView,
    AdoptionApplicationListView,
    update_application_status,
    adoption_application_detail,
    pet_detail,
    approve_all_applications,
    RequestShelterView,
)

urlpatterns = [
    # Dashboard home
    path('', DashboardHomeView.as_view(), name='dashboard'),

    # Pets
    path('pets/', PetListView.as_view(), name='dashboard-pets'),
    path('pets/add/', PetCreateView.as_view(), name='pet-add'),  # ✅ this is the name your template expects
    path('pets/<int:pk>/edit/', PetUpdateView.as_view(), name='pet-edit'),
    path('pets/<int:pk>/delete/', PetDeleteView.as_view(), name='pet-delete'),
    path('pets/<int:pk>/view/', pet_detail, name='dashboard-pet-detail'),
    path('pets/<int:pk>/approve_all/', approve_all_applications, name='dashboard-pet-approve-all'),

    # Adoption applications
    path('adoptions/', AdoptionApplicationListView.as_view(), name='dashboard-adoptions'),
    path('adoptions/<int:pk>/<str:status>/', update_application_status, name='dashboard-adoption-update'),
    path('adoptions/<int:pk>/', adoption_application_detail, name='dashboard-adoption-detail'),
    path('request-shelter/', RequestShelterView.as_view(), name='dashboard-request-shelter'),
]
