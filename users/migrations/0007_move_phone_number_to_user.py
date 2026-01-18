# Generated migration to move phone_number from Profile to User

from django.db import migrations, models


def migrate_phone_numbers_forward(apps, schema_editor):
    """Copy phone_number from Profile to User"""
    User = apps.get_model('users', 'User')
    Profile = apps.get_model('users', 'Profile')
    
    # Copy from Profile to User
    for profile in Profile.objects.all():
        if profile.user:
            profile.user.phone_number = profile.phone_number or ''
            profile.user.save()
    
    # For users without profiles, set empty string (will be required for new registrations)
    for user in User.objects.filter(phone_number__isnull=True):
        user.phone_number = ''
        user.save()


def migrate_phone_numbers_reverse(apps, schema_editor):
    """Copy phone_number back from User to Profile (for rollback)"""
    User = apps.get_model('users', 'User')
    Profile = apps.get_model('users', 'Profile')
    
    for user in User.objects.all():
        if hasattr(user, 'profile') and user.phone_number:
            profile = user.profile
            profile.phone_number = user.phone_number
            profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_student_linking_code_and_more'),
    ]

    operations = [
        # Step 1: Add phone_number to User as nullable
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, help_text='Required for registration', max_length=20, null=True, verbose_name='phone number'),
        ),
        
        # Step 2: Copy data from Profile to User
        migrations.RunPython(
            migrate_phone_numbers_forward,
            migrate_phone_numbers_reverse,
        ),
        
        # Step 3: Remove phone_number from Profile
        migrations.RemoveField(
            model_name='profile',
            name='phone_number',
        ),
        
        # Step 4: Make phone_number non-nullable on User (with empty string default for existing users)
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=False, default='', help_text='Required for registration', max_length=20, verbose_name='phone number'),
        ),
    ]

