from django.urls import path
from .views import signup, custom_login
from django.contrib.auth.views import LogoutView
from .views import admin_create_shelter

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', custom_login, name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),  # logs out to public UI
    path('admin/create-shelter/', admin_create_shelter, name='admin-create-shelter'),
]
