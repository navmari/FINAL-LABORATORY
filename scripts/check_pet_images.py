import os
import django
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PetConnect.settings')
django.setup()
from pets.models import Pet
from django.conf import settings

pets = Pet.objects.all()
print('Pet count:', pets.count())
for p in pets:
    name = p.pet_image.name if p.pet_image else '<no image>'
    path = os.path.join(settings.MEDIA_ROOT, name) if p.pet_image else '<no path>'
    exists = os.path.exists(path) if p.pet_image else False
    print(p.id, p.pet_name, name, exists, path)
