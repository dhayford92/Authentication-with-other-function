from django.contrib import admin
from .models import User, OtpCode




class UserAdmin(admin.ModelAdmin):
    list_display = ['fullname', 'email', 'phone', 'provider']
    class Meta:
        model = User
        
        
admin.site.register(User, UserAdmin)
admin.site.register(OtpCode)