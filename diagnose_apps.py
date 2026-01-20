import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PetConnect.settings')
django.setup()

from pets.models import AdoptionApplication

apps = AdoptionApplication.objects.select_related('pet', 'pet__shelter')
print('Total adoption applications:', apps.count())
for a in apps:
    pet = a.pet
    shelter_id = pet.shelter.id if pet and pet.shelter else None
    print(f'id={a.id} request_id={a.request_id} status={a.status} pet_id={a.pet_id} pet_name={getattr(pet, "pet_name", None)} shelter_id={shelter_id} created_at={a.created_at}')
