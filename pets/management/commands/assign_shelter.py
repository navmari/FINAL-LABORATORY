from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from pets.models import UserProfile, Shelter


class Command(BaseCommand):
    help = 'Assign a Shelter to a user or bulk-assign to all shelter-role users missing a shelter.'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username to assign')
        parser.add_argument('--shelter-id', type=int, help='ID of the Shelter to assign', required=True)
        parser.add_argument('--bulk', action='store_true', help='Assign the shelter to all users with role SHELTER missing a shelter')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without saving')

    def handle(self, *args, **options):
        username = options.get('username')
        shelter_id = options.get('shelter_id')
        bulk = options.get('bulk')
        dry = options.get('dry_run')

        try:
            shelter = Shelter.objects.get(pk=shelter_id)
        except Shelter.DoesNotExist:
            raise CommandError(f'Shelter with id {shelter_id} does not exist')

        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f'User {username} does not exist')

            profile = getattr(user, 'profile', None)
            if not profile:
                raise CommandError(f'User {username} has no profile')

            if dry:
                self.stdout.write(self.style.SUCCESS(f'Would assign shelter {shelter} to user {username}'))
                return

            profile.shelter = shelter
            profile.save()
            self.stdout.write(self.style.SUCCESS(f'Assigned shelter {shelter} to user {username}'))
            return

        if bulk:
            qs = UserProfile.objects.filter(role='SHELTER', shelter__isnull=True)
            count = qs.count()
            if count == 0:
                self.stdout.write('No users found that need assignment')
                return

            if dry:
                self.stdout.write(self.style.SUCCESS(f'Would assign shelter {shelter} to {count} users'))
                return

            qs.update(shelter=shelter)
            self.stdout.write(self.style.SUCCESS(f'Assigned shelter {shelter} to {count} users'))
            return

        raise CommandError('Provide --username or --bulk along with --shelter-id')
