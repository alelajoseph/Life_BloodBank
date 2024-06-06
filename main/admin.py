from django.contrib import admin
from .models import Otp, Appointment

# Register your models here.
admin.site.site_header = "Life_BloodBank Admin"
admin.site.site_title = "Life_BloodBank Admin Portal"
admin.site.index_title = "Welcome to Life_BloodBank Admin Portal"
admin.site.register(Otp)
admin.site.register(Appointment)
