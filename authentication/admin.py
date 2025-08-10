from django.contrib import admin
from .models import Login_model
# Register your models here.
@admin.register(Login_model)
class LoginModelAdmin(admin.ModelAdmin):
    list_display=('id','name','email')