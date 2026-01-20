import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PetConnect.settings')
django.setup()

from pets.models import UserProfile

print('UserProfiles (role, username, shelter_id, shelter_name):')
for p in UserProfile.objects.select_related('user', 'shelter'):
    uname = p.user.username if p.user else None
    shelter_id = p.shelter.id if p.shelter else None
    shelter_name = p.shelter.shelter_name if p.shelter else None
    print(f'user={uname} role={p.role} shelter_id={shelter_id} shelter_name={shelter_name}')
