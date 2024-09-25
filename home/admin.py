from django.contrib import admin
from .models import SiteConfiguration

# Register your models here.
from django.contrib import admin
from .models import SiteConfiguration

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'maintenance_mode']

    def has_add_permission(self, request):
        # Prevent more than one configuration from being added
        if SiteConfiguration.objects.exists():
            return False
        return True

