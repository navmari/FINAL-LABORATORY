from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pets.models import Shelter
from PIL import Image, ImageOps
import os


class Command(BaseCommand):
    help = 'Regenerate shelter logo main images and thumbnails for all shelters or a single shelter.'

    def add_arguments(self, parser):
        parser.add_argument('--id', type=int, help='Shelter ID to process (optional)')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be done without saving')

    def handle(self, *args, **options):
        sid = options.get('id')
        dry = options.get('dry_run')

        qs = Shelter.objects.all()
        if sid:
            qs = qs.filter(pk=sid)
            if not qs.exists():
                raise CommandError(f'Shelter with id {sid} does not exist')

        count = 0
        for shelter in qs:
            if not shelter.logo:
                self.stdout.write(self.style.NOTICE(f"Skipping shelter {shelter.pk} ({shelter}) - no logo."))
                continue

            logo_path = shelter.logo.path
            self.stdout.write(f"Processing shelter {shelter.pk} - {shelter.shelter_name}")

            try:
                with Image.open(logo_path) as img:
                    # Normalize to RGB and handle alpha channels
                    if img.mode in ('RGBA', 'LA'):
                        background = Image.new('RGBA', img.size, (255, 255, 255, 255))
                        background.paste(img, mask=img.split()[-1])
                        img = background.convert('RGB')
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')

                    # Only create/update thumbnail; keep original main image intact
                    thumb_size = getattr(settings, 'SHELTER_THUMB_SIZE', (128, 128))
                    quality = getattr(settings, 'SHELTER_IMAGE_QUALITY', 85)

                    if dry:
                        self.stdout.write(self.style.NOTICE(f"Would create thumb {thumb_size} for {shelter.pk}"))
                    else:
                        thumb_img = ImageOps.fit(img, thumb_size, Image.ANTIALIAS, centering=(0.5, 0.5))
                        media_root = settings.MEDIA_ROOT
                        thumb_rel_dir = os.path.join('shelters', 'thumbs')
                        thumb_dir = os.path.join(media_root, thumb_rel_dir)
                        os.makedirs(thumb_dir, exist_ok=True)

                        base, ext = os.path.splitext(os.path.basename(logo_path))
                        thumb_filename = f"{base}_thumb.jpg"
                        thumb_path = os.path.join(thumb_dir, thumb_filename)

                        thumb_img.save(thumb_path, optimize=True, quality=quality)

                        shelter.logo_thumb.name = os.path.join(thumb_rel_dir, thumb_filename).replace('\\', '/')
                        shelter.save(update_fields=['logo_thumb'])

                        self.stdout.write(self.style.SUCCESS(f"Processed shelter {shelter.pk}: thumb saved to {shelter.logo_thumb.name}"))

                count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing shelter {shelter.pk}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Done. Processed {count} shelters."))
