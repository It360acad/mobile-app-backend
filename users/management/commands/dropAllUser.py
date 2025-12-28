from django.core.management.base import BaseCommand
from users.models import User, Profile


class Command(BaseCommand):
    help = 'Delete all users and their profiles from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput',
            '--no-input',
            action='store_true',
            help='Do not prompt for confirmation',
        )

    def handle(self, *args, **options):
        user_count = User.objects.count()
        
        if user_count == 0:
            self.stdout.write(self.style.WARNING('No users found in the database.'))
            return

        if not options['noinput']:
            confirm = input(
                f'This will delete {user_count} user(s) and their profiles. '
                'Are you sure you want to continue? (yes/no): '
            )
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.WARNING('Operation cancelled.'))
                return

        # Delete all profiles first (due to foreign key relationship)
        profile_count = Profile.objects.count()
        Profile.objects.all().delete()
        
        # Delete all users
        User.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {user_count} user(s) and {profile_count} profile(s).'
            )
        )

