from django.urls import path
from .views import home, role_based_redirect, adopt_pet, application_detail, pet_tips, pet_tip_detail, pet_detail, my_applications, about

urlpatterns = [
    path('', home, name='home'),  # Public system UI
    path('about/', about, name='about'),  # About page with shelters
    path('redirect/', role_based_redirect, name='role-redirect'),  # Post-login redirect
    path('pets/<int:pk>/adopt/', adopt_pet, name='adopt-pet'),
    path('pets/<int:pk>/', pet_detail, name='pet-detail'),
    path('applications/<int:pk>/', application_detail, name='application-detail'),
    path('my-applications/', my_applications, name='my-applications'),  # Adopter view their applications
    path('tips/', pet_tips, name='pet-tips'),
    path('tips/<int:pk>/', pet_tip_detail, name='pet-tip-detail'),
]
