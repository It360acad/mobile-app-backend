from django.contrib import admin
from .models import User, Profile, Student, Parent

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone_number', 'role', 'is_verified', 'is_staff')
    search_fields = ('email', 'phone_number')
    list_filter = ('role', 'is_verified', 'is_staff')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'country')
    search_fields = ('user__email', 'user__phone_number')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id')
    search_fields = ('user__email', 'student_id')

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__email',)
