from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Pet, PetLogHistory

@receiver(pre_delete, sender=Pet)
def create_history_on_delete(sender, instance, **kwargs):
    PetLogHistory.objects.create(
        pet=instance,
        name=instance.pet_name,
        species=instance.species,
        breed=instance.breed,
        age_years=instance.age_years,
        age_months=instance.age_months,
        description=instance.description,
        status=instance.status,
        date_added=instance.date_added,
        pet_image=instance.pet_image.url if instance.pet_image else ''
    )
