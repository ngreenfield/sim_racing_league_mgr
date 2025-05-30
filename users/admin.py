
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from leagues.models import LeagueRegistration  # Keep LeagueRegistration import

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('role',)
    list_filter = UserAdmin.list_filter + ('role',)
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs


@admin.register(LeagueRegistration)
class LeagueRegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'league', 'registered_at']
    list_filter = ['league', 'registered_at']
    search_fields = ['user__username', 'league__name']
    date_hierarchy = 'registered_at'
