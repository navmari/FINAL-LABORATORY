from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import datetime
import os
from django.conf import settings
from PIL import Image, ImageOps
from ckeditor.fields import RichTextField

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('SHELTER', 'Shelter Staff'),
        ('ADOPTER', 'Adopter'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=200)
   
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ADOPTER')
    created_at = models.DateTimeField(auto_now_add=True)
   
    def __str__(self):
        return f"{self.name} ({self.role})"

class UserLoginHistory(models.Model): 
    # User Login History has Many-to-One Relationship with UserProfile, since one user can have multiple Login records.   
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='login_history')
    login_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='SUCCESS')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_info = models.CharField(max_length=200, blank=True)
    
    class Meta:
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.name} - {self.login_time}"

class Shelter(models.Model):    
    shelter_name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='shelter_logos/', blank=True, null=True)
    logo_thumb = models.ImageField(upload_to='shelter_logos/thumbs/', blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    social_media_page = models.URLField(blank=True)
    description = models.TextField()
    date_registered = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.shelter_name

    def save(self, *args, **kwargs):
        # Ensure the instance is saved first so file paths are available
        already_processed = getattr(self, '_logo_processed', False)
        super().save(*args, **kwargs)

        # Only generate a thumbnail for the logo, do not alter the original image
        if self.logo and hasattr(self.logo, 'path'):
            try:
                img_path = self.logo.path
                with Image.open(img_path) as img:
                    # Normalize to RGB and handle alpha channels
                    if img.mode in ('RGBA', 'LA'):
                        background = Image.new('RGBA', img.size, (255, 255, 255, 255))
                        background.paste(img, mask=img.split()[-1])
                        img = background.convert('RGB')
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')

                    # Thumbnail: center-crop and resize using settings
                    thumb_size = getattr(settings, 'SHELTER_THUMB_SIZE', (128, 128))
                    quality = getattr(settings, 'SHELTER_IMAGE_QUALITY', 85)
                    thumb_img = ImageOps.fit(img, thumb_size, Image.ANTIALIAS, centering=(0.5, 0.5))

                    # Prepare thumb path
                    media_root = settings.MEDIA_ROOT
                    thumb_rel_dir = os.path.join('shelter_logos', 'thumbs')
                    thumb_dir = os.path.join(media_root, thumb_rel_dir)
                    os.makedirs(thumb_dir, exist_ok=True)

                    base, ext = os.path.splitext(os.path.basename(img_path))
                    thumb_filename = f"{base}_thumb.jpg"
                    thumb_path = os.path.join(thumb_dir, thumb_filename)

                    thumb_img.save(thumb_path, optimize=True, quality=quality)

                    # Update model field to point to thumb (relative path) and save that field only
                    self.logo_thumb.name = os.path.join(thumb_rel_dir, thumb_filename).replace('\\', '/')
                    super().save(update_fields=['logo_thumb'])
            except Exception:
                # Fail silently; don't prevent model save if image processing fails
                pass

UserProfile.add_to_class(
    'shelter',# Adding Shelter ForeignKey to UserProfile for Shelter Staff Association
    # A Shelter can have multiple users as staff but each UserProfile can be assocaited with only one Shelter.
    models.ForeignKey(Shelter, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff')
)

class Pet(models.Model):    
    SPECIES_CHOICES = [
        ('DOG', 'Dog'),
        ('CAT', 'Cat'),
        ('BIRD', 'Bird'),
        ('OTHER', 'Other'),
    ]

    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('UNKNOWN', 'Unknown'),
    ]

    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('ADOPTED', 'Adopted'),
        ('PENDING', 'Pending'),
    ]
    pet_name = models.CharField(max_length=100)
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES)
    breed = models.CharField(max_length=100)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='UNKNOWN')
    age_years = models.IntegerField(validators=[MinValueValidator(0)])
    age_months = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    health_status = models.TextField()
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    adoption_fee = models.DecimalField(max_digits=10, decimal_places=2)   
    pet_image = models.FileField(upload_to='pet_images/', blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)    
   # Shelter can have multiple Pets but each Pet belongs to only one shelter.
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='pets')
    
    def __str__(self):
        return f"{self.pet_name} ({self.species})"
    
class PetLogHistory(models.Model):     
    # Pet has One-to-Many relationship with PetHistory since on pet ca have multiple history records sir and I also added a history_id for this so that even if the pet record is deleted in pet table, it can still be saved in petloghistory table for some purposes.
    pet = models.ForeignKey(Pet, on_delete=models.SET_NULL, null=True, blank=True, related_name='history')
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=20)
    breed = models.CharField(max_length=100)
    age_years = models.IntegerField()
    age_months = models.IntegerField()
    description = models.TextField()
    status = models.CharField(max_length=20)
    date_added = models.DateTimeField()
    pet_image = models.CharField(max_length=500, blank=True)
    deleted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-deleted_at']
    
    def __str__(self):
        return f"History: {self.name} - {self.deleted_at}"

class AdoptionApplication(models.Model):
    # =========================
    # Status Constants
    # =========================
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    COMPLETED = 'COMPLETED'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (COMPLETED, 'Completed'),
    ]

    request_id = models.CharField(max_length=50, unique=True, editable=False)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='applications')
    
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    
    # Pet Details (from application)
    pet_name = models.CharField(max_length=100)
    pet_image = models.FileField(upload_to='adoption_images/', blank=True, null=True)
    reason_for_adoption = models.TextField()
    
    # Application Status Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.request_id:
            import datetime
            # Generate unique request ID based on timestamp to avoid collisions
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            self.request_id = f"REQ-{timestamp}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.request_id} - {self.first_name} {self.last_name}"


class PetCareTip(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextField()
    image = models.ImageField(upload_to='care_tips/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
