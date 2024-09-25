from django.contrib import admin # type: ignore
from .models import *

# Registering models for the admin interface
admin.site.register(Recipe)
admin.site.register(Rating)
admin.site.register(Comment)
admin.site.register(UserProfile)
